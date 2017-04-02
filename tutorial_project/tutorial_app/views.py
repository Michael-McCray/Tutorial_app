from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User 
from models import Category, Page, UserProfile
from forms import CategoryForm, PageForm, UserForm, UserProfileForm, ContactForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from search import run_query
from suggest import get_category_list



def index(request):
    
    #  Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    
    # Render the response and send it back!
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False
    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - last_visit_time).seconds > 0:
            visits = visits + 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True
    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits
    return render(request, 'index.html', context_dict)

def about(request):
    context_dict = {}
    
    if request.session.get('visits'):
        count = int(request.session.get('visits'))
    else:
        count = 0
    count = count + 1
    context_dict['visits'] = count

    return render(request, 'about.html', context_dict)


def category(request, category_name_slug):
    
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')
        
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    if not context_dict['query']:
        context_dict['query'] = category.name

    # Go render the response and return it to the client.
    return render(request, 'category.html', context_dict)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.send_message()

            return HttpResponseRedirect('/')
        else:
            print form.errors
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form':form})

def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with =  request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    print cat_list

    return render(request, 'cats.html', {'cats': cat_list })

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form':form})

@login_required
def auto_page_add(request):
    cat_id = None
    url = None
    title = None
    user = None
    context_dict = {}

    if request.method == 'GET':
        cat_id =  request.GET['category_id']
        url =  request.GET['url']
        title = request.GET['title']
        user = request.GET['user']

        if cat_id and user:
            category = Category.objects.get(id=int(cat_id))
            user = User.objects.get(username=user)
            p = Page.objects.get_or_create(category=category, title=title, url=url, user=user)

            pages = Page.objects.filter(category=category).order_by('-views')

            context_dict['pages'] = pages

    return render(request, 'page_list.html', context_dict)

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)

@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)

    except Category.DoesNotExist:
            cat = None

    if request.method == 'POST':
        form =  PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.user = request.user # add
                page.views = 0
                page.save()
                return category(request, category_name_slug)
            else:
                print form.errors
        else:
            print form.errors
    else:
        form = PageForm()
    context_dict = {'form':form, 'category': cat, 'slug': category_name_slug}

    return render(request, 'add_page.html', context_dict)

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,
            'register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'login.html', {})
# Use the login_required() decorator to ensure only those logged in can access the view.

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')

def track_url(request):
    page_id = None
    url = '/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)

def user_profile(request, user_username):
    context_dict = {}
    user = User.objects.get(username=user_username)
    profile = UserProfile.objects.get(user=user)
    context_dict['profile'] = profile
    context_dict['pages'] = Page.objects.filter(user=user)

    return  render(request, 'profile.html', context_dict)

@login_required
def edit_profile(request, user_username):
    profile = get_object_or_404(UserProfile, user__username=user_username)
    website = profile.website
    pic = profile.picture
    bio = profilr.bio

    if request.user != profile.user: 
        return HttpResponse('Access Denied')

    if request.method == 'POST':
        form =  UserProfileForm(data=request.POST)
        if form.is_valid():

            if request.POST['website'] and request.POST['website'] != '':
                profile.website = request.POST['website']
            else:
                profile.website = website

            if request.POST['bio'] and request.POST['bio'] != '':
                profile.bio = request.POST['bio']
            else:
                profile.bio = bio

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            else:
                profile.picture = pic
            profile.save()

            return user_profile(request, profile.user.username)

        else:
            print form.errors

    else:
        form = UserProfileForm()

    return render(request, 
                'edit_profile.html', 
                {'form':form, 'profile': profile})