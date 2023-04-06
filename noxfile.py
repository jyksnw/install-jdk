import nox

@nox.session
def tests(session):
    session.install("-r", "requirements.txt")
    session.run('pytest')