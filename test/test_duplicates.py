import pytest
from rpmlint.checks.DuplicatesCheck import DuplicatesCheck
from rpmlint.filter import Filter

from Testing import CONFIG, get_tested_mock_package, get_tested_package


@pytest.fixture(scope='function', autouse=True)
def duplicatescheck():
    CONFIG.info = True
    output = Filter(CONFIG)
    test = DuplicatesCheck(CONFIG, output)
    return output, test


@pytest.mark.parametrize('package', [get_tested_mock_package(
    files={
            '/etc/bar': {'content': 'large enough file', 'metadata': {'mode': 33188}},
            '/etc/bar2': {'content': 'large enough file', 'metadata': {'mode': 33188}},
            '/etc/bar3': {'content': 'large enough file', 'metadata': {'mode': 33188}},
            '/etc/foo': {'content': 'Foo file', 'metadata': {'mode': 33188}},
            '/etc/foo2': {'content': 'Foo 2 file', 'metadata': {'mode': 33188, 'flags': 1}},
            '/etc/small': {'content': ' \n', 'metadata': {'mode': 33188}},
            '/etc/small2': {'content': ' \n', 'metadata': {'mode': 33188}},
            '/var/foo': {'content': 'Foo file', 'metadata': {'mode': 33188}},
            '/var/foo2': {'content': 'Foo 2 file', 'metadata': {'mode': 33188, 'flags': 1}}
    },
    real_files=True
)])
def test_duplicates1(package, duplicatescheck):
    output, test = duplicatescheck
    test.check(package)
    out = output.print_results(output.results)

    # assert 'E: hardlink-across-partition /var/foo /etc/foo' in out
    assert 'E: hardlink-across-config-files /var/foo2 /etc/foo2' in out
    assert 'W: files-duplicate /etc/bar3 /etc/bar:/etc/bar2' in out
    assert 'W: files-duplicate /etc/strace2.txt /etc/strace1.txt' in out
    assert 'W: files-duplicate /etc/small2 /etc/small' not in out
    assert 'E: files-duplicated-waste 270544' in out


@pytest.mark.parametrize('package', ['binary/duplicates'])
def test_duplicates(tmp_path, package, duplicatescheck):
    output, test = duplicatescheck
    test.check(get_tested_package(package, tmp_path))
    out = output.print_results(output.results)

    assert 'E: hardlink-across-partition /var/foo /etc/foo' in out
    assert 'E: hardlink-across-config-files /var/foo2 /etc/foo2' in out
    assert 'W: files-duplicate /etc/bar3 /etc/bar:/etc/bar2' in out
    assert 'W: files-duplicate /etc/strace2.txt /etc/strace1.txt' in out
    assert 'W: files-duplicate /etc/small2 /etc/small' not in out
    assert 'E: files-duplicated-waste 270544' in out


@pytest.mark.parametrize('package', ['binary/bad-crc-uncompressed'])
def test_duplicates_correct(tmp_path, package, duplicatescheck):
    output, test = duplicatescheck
    test.check(get_tested_package(package, tmp_path))
    out = output.print_results(output.results)

    assert 'E: hardlink-across-partition' not in out
    assert 'E: hardlink-across-config-files' not in out
    assert 'W: files-duplicate' not in out
    assert 'E: files-duplicated-waste' not in out
