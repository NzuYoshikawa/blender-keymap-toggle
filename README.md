# Keymap Toggle

A Blender add-on that instantly switches between the **Blender** keymap and the **Industry Compatible** keymap using a single shortcut key.

---

## Requirements

- Blender 3.0 or later

---

## Installation

1. Download **`keymap_toggle.zip`** from the [Latest Release](https://github.com/NzuYoshikawa/blender-keymap-toggle/releases/latest)
2. Open `Edit > Preferences > Add-ons`
3. Click `Install...`, select `keymap_toggle.zip`, then click `Install Add-on`
4. Enable **Keymap Toggle** by checking the checkbox in the list

---

## Usage

Once enabled, the add-on automatically scans both keymaps and assigns a **conflict-free shortcut key** (typically `Ctrl+Shift+Alt+A`).

Press the assigned key to toggle between keymaps:

- **Blender → Industry Compatible**
- **Industry Compatible → Blender**

A notification message appears in the bottom left of the screen on each switch:

```
Keymap switched to: Industry Compatible
```

---

## Preferences

Open `Edit > Preferences > Add-ons > Keymap Toggle` to access the settings panel.

### Current Keymap Display

The currently active keymap name is shown in the box at the top of the panel.

### Changing the Shortcut Key

| Control | Description |
|---|---|
| `Ctrl` / `Shift` / `Alt` toggle buttons | Enable or disable modifier keys |
| Key input field | Enter the key to use (e.g. `K`, `F5`) |
| **Apply Shortcut** button | Checks for conflicts and registers the new shortcut |
| **Auto-detect conflict-free key** button | Scans both keymaps and automatically assigns a conflict-free key |

> If a conflict is detected, a warning message is shown and the change is not applied. Please try a different key.

---

## Notes

- Shortcut key settings are preserved after restarting Blender
- The active keymap is also restored after restart
- If keymap names differ between Blender versions, the add-on automatically falls back to a partial name search
- If an error occurs after switching, run the following in the Blender Script Console to check available keyconfig names:

```python
for kc in bpy.context.window_manager.keyconfigs:
    print(kc.name)
```

---

## Changelog

| Version | Changes |
|---|---|
| 1.0.1 | Fixed keymap switch not applying immediately |
| 1.0.0 | Initial release |

---

---

# Keymap Toggle（日本語）

Blender の「Blender 標準キーマップ」と「業界互換キーマップ」を、ショートカットキー一発で瞬時に切り替えるアドオンです。

---

## 動作環境

- Blender 3.0 以上

---

## インストール

1. [最新のRelease](https://github.com/NzuYoshikawa/blender-keymap-toggle/releases/latest) から **`keymap_toggle.zip`** をダウンロード
2. `Edit > Preferences > Add-ons` を開く
3. `Install...` をクリックし、`keymap_toggle.zip` を選択して `Install Add-on` をクリック
4. リストに表示された **Keymap Toggle** のチェックボックスをオンにして有効化

---

## 基本的な使い方

有効化すると、両方のキーマップを自動スキャンして**衝突しないショートカットキーが自動で割り当てられます**（デフォルトは `Ctrl+Shift+Alt+A` になることが多いです）。

割り当てられたキーを押すたびに、キーマップがトグル切り替えされます。

- **Blender → Industry Compatible**
- **Industry Compatible → Blender**

切り替えのたびに画面左下に通知メッセージが表示されます。

```
Keymap switched to: Industry Compatible
```

---

## Preferences パネル

`Edit > Preferences > Add-ons > Keymap Toggle` を開くと設定パネルが表示されます。

### 現在のキーマップ表示

パネル上部のボックスに、現在アクティブなキーマップ名が表示されます。

### ショートカットキーの変更

| 操作 | 説明 |
|---|---|
| `Ctrl` / `Shift` / `Alt` トグルボタン | 修飾キーのオン/オフを切り替え |
| キー入力欄 | 使用するキーを入力（例：`K`、`F5`） |
| **Apply Shortcut** ボタン | 入力した組み合わせの衝突チェックを行い、問題なければ登録 |
| **Auto-detect conflict-free key** ボタン | 両キーマップを再スキャンし、衝突のないキーを自動検出して登録 |

> 衝突が検出された場合は警告メッセージが表示され、変更は適用されません。別のキーを試してください。

---

## 注意事項

- ショートカットキーの設定はBlenderを再起動しても保持されます
- キーマップの切り替えも再起動後に維持されます
- Blenderのバージョンによってキーマップ名が異なる場合、アドオンが自動的に部分一致で検索します
- 切り替え後にエラーが表示された場合は、スクリプトコンソールで以下を実行してキーマップ名を確認してください

```python
for kc in bpy.context.window_manager.keyconfigs:
    print(kc.name)
```

---

## バージョン履歴

| バージョン | 内容 |
|---|---|
| 1.0.1 | キーマップ切り替えが即時反映されないバグを修正 |
| 1.0.0 | 初回リリース |
