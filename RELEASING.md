# Release checklist

Jazzband guidelines: https://jazzband.co/about/releases

- [ ] Get master to the appropriate code release state.
      [Travis CI](https://travis-ci.org/jazzband/prettytable) and
      [GitHub Actions](https://github.com/jazzband/prettytable/actions) should pass on
      master.
      [![Travis CI Status](https://img.shields.io/travis/jazzband/prettytable/master?label=Travis%20CI&logo=travis)](https://travis-ci.org/jazzband/prettytable)
      [![GitHub Actions status](https://github.com/jazzband/prettytable/workflows/Test/badge.svg)](https://github.com/jazzband/prettytable/actions)

- [ ] Edit release draft, adjust text if needed:
      https://github.com/jazzband/prettytable/releases

- [ ] Check next tag is correct, amend if needed

- [ ] Publish release

- [ ] Once
      [GitHub Actions](https://github.com/jazzband/prettytable/actions?query=workflow%3ADeploy)
      has built and uploaded distributions, check files at
      [Jazzband](https://jazzband.co/projects/prettytable) and release to
      [PyPI](https://pypi.org/pypi/prettytable)

- [ ] Check installation:

```bash
pip uninstall -y prettytable
pip install -U prettytable
python3 -c "import prettytable; print(prettytable.__version__)"
```
