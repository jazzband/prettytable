# Release checklist

Jazzband guidelines: https://jazzband.co/about/releases

* [ ] Get master to the appropriate code release state.
      [Travis CI](https://travis-ci.org/jazzband/prettytable) and
      [GitHub Actions](https://github.com/jazzband/prettytable/actions)
      should pass on master.
      [![Travis CI Status](https://img.shields.io/travis/jazzband/prettytable/master?label=Travis%20CI&logo=travis)](https://travis-ci.org/jazzband/prettytable)
      [![GitHub Actions status](https://github.com/jazzband/prettytable/workflows/Test/badge.svg)](https://github.com/jazzband/prettytable/actions)

- [ ] Check
      [CHANGELOG.md](https://github.com/jazzband/prettytable/blob/master/CHANGELOG.md),
      update version number and release date

* [ ] Tag with version number and push tag, for example:
```bash
git tag -a 1.0.0 -m "Release 1.0.0"
git push --tags
```

* [ ] Once Travis CI has built and uploaded distributions, check files at
      [Jazzband](https://jazzband.co/projects/prettytable) and release to
      [PyPI](https://pypi.org/pypi/prettytable)

* [ ] Check installation:
```bash
pip uninstall -y prettytable
pip install -U prettytable
python3 -c "import prettytable; print(prettytable.__version__)"
```

* [ ] Create new GitHub release: https://github.com/jazzband/prettytable/releases/new
  * Tag: Pick existing tag "1.0.0"
