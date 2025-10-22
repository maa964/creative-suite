import os
import io
import time
import base64
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

def _is_base64_image(s: str) -> bool:
    return isinstance(s, str) and s.startswith('data:image') and 'base64,' in s

def _load_image(input_path_or_data: str):
    from PIL import Image
    if _is_base64_image(input_path_or_data):
        try:
            header, b64 = input_path_or_data.split('base64,', 1)
            data = base64.b64decode(b64)
            return Image.open(io.BytesIO(data)).convert('RGB')
        except Exception as e:
            LOG.exception('failed to load base64 image: %s', e)
            raise ValueError('invalid base64 image data') from e
    else:
        p = Path(input_path_or_data)
        if not p.exists():
            raise FileNotFoundError(f'input file not found: {input_path_or_data}')
        from PIL import Image
        return Image.open(str(p)).convert('RGB')

def _save_image(img, output_path: str):
    outp = Path(output_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(outp))
    return str(outp)

def _heuristic_colorize(pil_img):
    """単純なヒューリスティックによる擬似カラー化。
    （実用モデルがない環境でのフォールバック）
    - グレースケールならRGBに変換して疑似カラーを重ねる
    - エッジを強調して色マップを合成する
    """
    from PIL import Image, ImageFilter, ImageOps
    import numpy as np

    gray = ImageOps.grayscale(pil_img)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    arr = np.array(pil_img).astype('float32') / 255.0
    e = np.array(edges).astype('float32') / 255.0
    # ランダムではなく、チャンネルに差を付ける簡易処理
    r = np.clip(arr[:,:,0] * (0.8 + 0.4*e), 0, 1.0)
    g = np.clip(arr[:,:,1] * (0.9 + 0.3*e), 0, 1.0)
    b = np.clip(arr[:,:,2] * (0.7 + 0.5*e), 0, 1.0)
    out = (np.dstack([r,g,b]) * 255.0).astype('uint8')
    return Image.fromarray(out)

def _model_colorize(pil_img, timeout=30):
    """ローカルに diffusers 等のモデルがある場合に呼び出す想定のラッパー。
    実行環境に model ライブラリが無ければ ImportError を出す。
    """
    # 実装はプラグイン環境に合わせて差し替え。ここではダミーでヒューリスティックを呼ぶ。
    try:
        # placeholder for model inference
        # from diffusers import StableDiffusion...  (省略)
        # result = model.infer(...)
        # return result_image
        LOG.info('model colorize requested - but no model code present, falling back to heuristic')
        return _heuristic_colorize(pil_img)
    except Exception as e:
        LOG.exception('model colorize failed: %s', e)
        raise

def colorize_job(input_path: str, output_path: str, method: str='auto', timeout:int=60):
    """エントリポイント。例外は呼び出し元でキャッチしてください。
    入力検証／タイムアウト／ログ出力を行います。
    """
    start = time.time()
    LOG.info('colorize_job start input=%s output=%s method=%s', input_path, output_path, method)
    if not input_path or not output_path:
        raise ValueError('input_path and output_path are required')
    try:
        img = _load_image(input_path)
    except Exception as e:
        LOG.exception('load failed: %s', e)
        raise

    try:
        if method == 'model':
            out_img = _model_colorize(img)
        elif method == 'heuristic':
            out_img = _heuristic_colorize(img)
        else: # auto
            try:
                out_img = _model_colorize(img)
            except Exception:
                out_img = _heuristic_colorize(img)

        saved = _save_image(out_img, output_path)
        elapsed = time.time() - start
        LOG.info('colorize_job done saved=%s elapsed=%.2f', saved, elapsed)
        return {'status':'ok','output_path': saved, 'elapsed': elapsed}
    except Exception as e:
        LOG.exception('processing failed: %s', e)
        raise

# Plugin register API
def register(app_api=None):
    """ホストが呼び出す register(app_api)。
    app_api はホストが提供する簡易API（辞書相当）を想定。
    register の責務：
    - 自身の manifest を返すか、ホストへ登録を行う
    - 必要な依存チェック（例: pillow）を行い、問題があれば例外を投げる
    """
    # minimal validation and environment check
    try:
        import PIL
    except Exception as e:
        LOG.exception('Pillow is required for sample_plugin_ai: %s', e)
        raise RuntimeError('Pillow (PIL) is required for sample_plugin_ai') from e
    LOG.info('sample_plugin_ai registered with app_api=%s', getattr(app_api, 'name', str(app_api)))
    manifest = {
        'name': 'sample_plugin_ai',
        'version': '0.1.0',
        'commands': ['colorize']
    }
    return manifest
