import nox
import sys


@nox.session(python=["3.6", "3.7", "3.8", "3.9", "3.10", "3.11"])
def tests(session):
    if sys.version_info < (3, 6):
        session.skip("Tests require Python 3.6 or later.")
    session.install("-r", "requirements.txt")
    session.run('pytest')
