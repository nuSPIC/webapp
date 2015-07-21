# from .tasks import SimulationTask
#
# SimulationTask.delay(96)

from django.test import TestCase
from accounts.models import User
from .models import SPIC, Network

user = {
    'username':     'username',
    'first_name':   'Max',
    'last_name':    'Mustermann',
    'email':        'foo@example.com',
    'password':     'password',
}

spic = {
    'group':        0,
    'local_id':     1,
    'title' :       'Test',
}

network = {
    'local_id':     1,
}

class SPICTestCase(TestCase):
    def setUp(self):
        SPIC.objects.create(**spic)

    def test_field_title(self):
        spic_obj = SPIC.objects.get(id=1)
        self.assertEqual(spic_obj.title, spic['title'])

    def test_field_BooleanField(self):
        spic_obj = SPIC.objects.get(id=1)
        self.assertFalse(spic_obj.solution)

    def test_func_tooltip(self):
        spic_obj = SPIC.objects.get(id=1)
        self.assertEqual(spic_obj.tooltip(), {})

    def test_func_msg(self):
        spic_obj = SPIC.objects.get(id=1)
        self.assertEqual(spic_obj.msg(), {})


class NetworkTestCase(TestCase):
    def setUp(self):
        user_obj = User.objects.create(**user)
        SPIC_obj = SPIC.objects.create(**spic)
        network.update({'user_id': user_obj.id, 'SPIC_id':SPIC_obj.id})
        Network.objects.create(**network)

    def test_field_user_id(self):
        user_obj = User.objects.get(id=1)
        network_obj = Network.objects.get(user_id=user_obj.id)
        self.assertEqual(network_obj.user_id, user_obj.id)

    def test_field_SPIC(self):
        SPIC_obj = SPIC.objects.get(id=1)
        network_obj = Network.objects.get(SPIC_id=SPIC_obj.id)
        self.assertEqual(network_obj.SPIC_id, SPIC_obj.id)

    def test_field_local_id(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.local_id, network['local_id'])

    def test_field_empty_fields(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.voltmeter_json, '')
        self.assertEqual(network_obj.spike_detector_json, '')
        self.assertEqual(network_obj.status_json, '')

    def test_field_bool(self):
        network_obj = Network.objects.get(id=1)
        self.assertFalse(network_obj.has_voltmeter)
        self.assertFalse(network_obj.has_spike_detector)
        self.assertFalse(network_obj.favorite)
        self.assertFalse(network_obj.deleted)

    def test_func_latest_local_id(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.get_latest_local_id(), network['local_id'])

    def test_func_create_latest(self):
        network_obj = Network.objects.get(id=1)
        next_obj = network_obj.create_latest()
        self.assertEqual(next_obj.local_id, network['local_id']+1)

    def test_next_field_bool(self):
        network_obj = Network.objects.get(id=1)
        next_obj = network_obj.create_latest()
        self.assertFalse(next_obj.has_voltmeter)
        self.assertFalse(next_obj.has_spike_detector)
        self.assertFalse(next_obj.favorite)
        self.assertFalse(next_obj.deleted)

    def test_func_user(self):
        user_obj = User.objects.get(id=1)
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.user(), user_obj)

    def test_func_root_status(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.root_status(), {})

    def test_func_nodes(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.nodes(), [])

    def test_func_neuron_ids(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.neuron_ids(), [])

    def test_func_links(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.links(), [])

    def test_func_is_recorded(self):
        network_obj = Network.objects.get(id=1)
        self.assertFalse(network_obj.is_recorded())

    def test_func_spike_detector_data(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.spike_detector_data(), {'meta': {'connect_to': [], 'neurons': [], 'simTime': 1000.0}})
        next_obj = network_obj.create_latest()
        self.assertEqual(next_obj.spike_detector_data(), {'meta': {'connect_to': [], 'neurons': [], 'simTime': 1000.0}})

    def test_func_voltmeter_data(self):
        network_obj = Network.objects.get(id=1)
        self.assertEqual(network_obj.voltmeter_data(), {'meta': {'connect_to': [], 'neurons': [] }})
        next_obj = network_obj.create_latest()
        self.assertEqual(next_obj.voltmeter_data(), {'meta': {'connect_to': [], 'neurons': [] }})
