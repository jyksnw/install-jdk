from jdk.client.adoptium import (
    AdoptiumEnvironment,
    AdoptiumVendor,
    AdoptiumJvmImpl,
    AdoptiumClient,
)

from jdk.client.corretto import (
    CorrettoEnvironment,
    CorrettoOperatingSystem,
    CorrettoClient,
)

from jdk.client.client import load_client