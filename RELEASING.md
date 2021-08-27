# Release checklist

Jazzband guidelines: https://jazzband.co/about/releases

- [ ] Get master to the appropriate code release state.
      [GitHub Actions](https://github.com/jazzband/prettytable/actions) should pass on
      master.
      [![GitHub Actions status](https://github.com/jazzband/prettytable/workflows/Test/badge.svg)](https://github.com/jazzband/prettytable/actions)

- [ ] Edit release draft, adjust text if needed:
      https://github.com/jazzband/prettytable/releases

- [ ] Check next tag is correct, amend if needed

- [ ] Publish release

- [ ] Once
      [GitHub Actions](https://github.com/jazzband/prettytable/actions/workflows/release.yml)
      has built and uploaded distributions, check files at
      [Jazzband](https://jazzband.co/projects/prettytable) and release to
      [PyPI](https://pypi.org/pypi/prettytable)

- [ ] Check installation:

```bash
pip uninstall -y prettytable
pip install -U prettytable
python3 -c "import prettytable; print(prettytable.__version__)"
```
