import os
import tempfile
from pathlib import Path
from plugins import sample_plugin_ai, sample_plugin

def test_register_plugins():
    # register should return manifest-like dict
    manifest_ai = sample_plugin_ai.plugin.register(app_api={'name':'testhost'})
    assert isinstance(manifest_ai, dict)
    assert 'name' in manifest_ai and 'commands' in manifest_ai

    manifest_sample = sample_plugin.plugin.register(app_api={'name':'testhost'})
    # sample_plugin.register prints but may return None; just ensure it's importable
    assert manifest_sample is None or isinstance(manifest_sample, dict)

def test_colorize_job_creates_output(tmp_path):
    # create a small grayscale image
    from PIL import Image
    img_path = tmp_path / "in_gray.png"
    out_path = tmp_path / "out_color.png"
    img = Image.new('L', (64,64), color=128)  # gray
    img.save(img_path)

    res = sample_plugin_ai.plgitugin.colorize_job(str(img_path), str(out_path), method='heuristic')
    assert res.get('status') == 'ok'
    assert Path(res.get('output_path')).exists()
