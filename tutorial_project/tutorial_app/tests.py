from django.test import TestCase
from models import Category
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse




def add_user(username='test', email='test@test.com', password='test'):
 	u = User(username=username, email=email, password=password)
 	u.set_password(u.password)
 	u.save()
 	return u

def add_cat(user, name, likes):
 	c = Category.objects.get_or_create(user=user, name=name)[0]
 	c.likes = likes
 	c.save()
 	return c


class CategoryMethodTest(TestCase):
 	def test_likes_are_positive(self):
		"""
		ensure_likes_are_positive should results True for categories where likes are zero or positive
 		"""
 		user = add_user()
 		cat = Category(user=user, name='test', likes=-1)
 		cat.save()
 		self.assertEqual((cat.likes>=0), True)

 	def test_slug_line_creation(self):
 		user = add_user()
 		cat = Category(user=user, name='Random Cat String')
 		cat.save()
 		self.assertEqual(cat.slug, 'random-cat-string')

class IndexViewTest(TestCase):
 	def test_index_view_with_no_categories(self):
 		"""
         If no categories exist, an appropriate message should be displayed.
        """
 		response = self.client.get(reverse('index'))

 		self.assertEqual(response.status_code, 200)

 		self.assertContains(response, "There are no categories!")
 		self.assertQuerysetEqual(response.context['categories'], [])





	def test_index_view_with_categories(self):
	 
	 	user = add_user()
	 	add_cat(user, 'test',1)
	 	add_cat(user, 'temp',1)
	 	add_cat(user, 'tmp',1)
	 	add_cat(user, 'tmp test temp',1)

	 	response = self.client.get(reverse('index'))
	 	self.assertEqual(response.status_code, 200)
	 	self.assertContains(response, "tmp test temp")

	 	num_cats =len(response.context['categories'])
	 	self.assertEqual(num_cats , 4)
