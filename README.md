# install-jdk

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/309b149bb42643bbb08e01e6d0c553f9)](https://www.codacy.com/gh/jyksnw/install-jdk/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jyksnw/install-jdk&amp;utm_campaign=Badge_Grade)

This was originally a port of from the GitHub Action [`installjdk`](https://github.com/AdoptOpenJDK/install-jdk)

install-jdk aims to give you as many options as possible to install an OpenJDK Java version across a wide array of operating systems and architectures. Please see each vendors OpenJDK documentation to see what operating systems and architectures they support.

| OpenJDK Build | Status | Vendor Tags | Documentation |
| ------------- | ------ | ------- | ---- |
| Adoptium (default)          | Implemented     | Adoptium, Temuring, AdoptOpenJDK, eclipse | ...coming soon |
| Corretto            | Implemented     | Corretto, Amazon, AWS | ...coming soon |
| Microsoft            | Planning     | Microsoft | ...coming soon |
| Azul                  | Planning  | Azul, Zulu | ...coming soon |

install-jdk will do its best to detect the operating system and architecture that it is running on. Currently is able to detect:

* Operating Systems
  * Windows
  * Linux
  * MacOS
  * AIX

* Architecture
  * arm
  * aarch64
  * ppc64
  * x64
  * x86

## Install

```bash
pip install install-jdk
```

## Usage

```python
import jdk

jdk.install('11')
# Platform dependent install of Java JDK 11 into $HOME/.jdk/<VERSION>

jdk.install('11', jre=True)
# Platform dependent install of Java JRE 11 into $HOME/.jre/<VERSION>

print(jdk.OS)       # Detected platform operating system
print(jdk.ARCH)     # Detected platform CPU architecture

download_url = jdk.get_download_url('11')
print(download_url)
# Obtains the platform dependent JDK download url

download_url = jdk.get_download_url('11', jre=True)
print(download_url)
# Obtains the platform dependent JRE download url

jdk.uninstall('11')
# Removes the Java 11 JDK if installed

jdk.uninstall('11', jre=True)
# Removes the Java 11 JRE if installed

jdk.install('17', vendor='Corretto')
# Installs a Corretto build of Java 17 JDK. Defualt vendor is Adoptium
```

## Development

See [CONTRIBUTING](CONTRIBUTING.MD)