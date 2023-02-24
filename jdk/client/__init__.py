from jdk.client.adoptium import AdoptiumClient

# Must be kept at the bottom of the init file to ensure proper vendor loading
from jdk.client.client import load_client
from jdk.client.corretto import CorrettoClient
from jdk.client.zulu import ZuluClient
