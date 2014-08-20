from flask import request, redirect, render_template, url_for
from flask.views import MethodView
from CareerLog import app
from CareerLog.models import (Comments, Posts, Employment,
                              Education, Certification)
from flask_mongoengine.wtf import model_form
from operator import itemgetter


class PostView(MethodView):

    # pages can have forms for adding comments
    form = model_form(Comments, exclude=['created', 'modified'])

    def get_context(self, slug):
        post = Posts.objects.get_or_404(slug=slug)
        form = self.form(request.form)

        context = {
            "post": post,
            "form": form,
            "latest": Posts.objects.order_by('-created')[:10],
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('posts/post.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            comment = Comments()
            form.populate_obj(comment)

            post = context.get('post')
            post.comments.append(comment)
            post.save()

            return redirect(url_for('post', slug=slug))

        return render_template('posts/post.html', **context)


class PostList(MethodView):
    def __init__(self, filter_by=None, sort_field='-created', list_length=5):
        self.filter_by = filter_by
        self.sort_field = sort_field
        self.list_length = list_length

    def get_context(self, item):
        queryfilter = {}
        queryfilter['published'] = True
        if self.filter_by:
            queryfilter[self.filter_by] = item
        if self.sort_field:
            context = {
                "latest": Posts.objects(**queryfilter).order_by(
                    self.sort_field)[:self.list_length]
            }
        else:
            context = {
                "latest": Posts.objects(**queryfilter)[:self.list_length]
            }
        if self.filter_by:
            context['listtitle'] = "Posts by %s '%s'" % (self.filter_by, item)
        else:
            context['listtitle'] = "Latest Posts"
        return context

    def get(self, item=None):
        context = self.get_context(item)
        return render_template('posts/list.html', **context)


class ListValues(MethodView):
    def __init__(self, by_field, value_name, next_endpoint):
        self.by_field = by_field
        self.value_name = value_name
        self.next_endpoint = next_endpoint

    def get(self):
        value_count = Posts.objects.item_frequencies(self.by_field)
        sorted_values = sorted(
            value_count.iteritems(), key=itemgetter(1), reverse=True)
        return render_template(
            'valuelist.html', valuelist=sorted_values,
            valuename=self.value_name, next_endpoint=self.next_endpoint)


class ResumeView(MethodView):

    def get_context(self):
        employment = Employment.objects.all()
        education = Education.objects.all()
        certification = Certification.objects.all().order_by("-priority")
        context = {
            "employment": employment,
            "education": education,
            "certification": certification
        }
        return context

    def get(self):
        context = self.get_context()
        return render_template('resume.html', **context)


# a view to show post categories
app.add_url_rule('/categories/', view_func=ListValues.as_view(
    'categorylist', by_field='category', value_name='categories',
    next_endpoint='by_category'))

# a view to show post tags
app.add_url_rule('/tags/', view_func=ListValues.as_view(
    'taglist', by_field='tags', value_name='tags',
    next_endpoint='by_tag'))

# a view to show dates for posts
app.add_url_rule('/posts/', view_func=PostList.as_view(
    'posts', sort_field='-created', list_length=10))

app.add_url_rule('/', defaults={'slug': 'home'}, view_func=PostView.as_view(
    'home'))

# list all posts by certain category
app.add_url_rule('/categories/<item>/', view_func=PostList.as_view(
    'by_category', filter_by='category'))

# list all posts by tag
app.add_url_rule('/tags/<item>/', view_func=PostList.as_view(
    'by_tag', filter_by='tags', sort_field='-created', list_length=4))

app.add_url_rule('/<slug>/', view_func=PostView.as_view('post'))

app.add_url_rule('/resume/', view_func=ResumeView.as_view('resume'))
