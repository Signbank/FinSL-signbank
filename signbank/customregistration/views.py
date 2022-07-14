from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_str
from django_registration.backends.activation import views


class ActivationView(views.ActivationView):
	def render_to_response(self, context_data):
		if context_data['activation_error']['code'] == 'already_activated':
			return HttpResponseRedirect(reverse('django_registration_activation_complete'))
		else:
			return super(ActivationView, self).render_to_response(context_data)
