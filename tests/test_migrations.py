import os


def test_patch_10a_file_exists():
    assert os.path.exists(os.path.join('migrations','versions','patch_10a_admin_cleanup.py'))


def test_patch_10a_has_upgrade_and_downgrade():
    path = os.path.join('migrations','versions','patch_10a_admin_cleanup.py')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert 'def upgrade()' in content
    assert 'def downgrade()' in content
