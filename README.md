# 微信表情工作室 · WeChat Sticker Studio

一个可复用的 Codex Skill：从 brainstorm、创建个人微信表情、修改定稿，到生成投稿物料、上传和跟进审核。

## 可以做什么

- 根据照片、原创角色或已有表情，讨论画风、名称与聊天场景。
- 生成统一形象的表情，按反馈修改，并复用要求保留的单图。
- 拆分规则网格合集，导出透明 PNG / 静态 GIF、缩略图、封面、图标与横幅。
- 检查尺寸、透明背景、文件大小及安全边距，打包素材与上传文案。
- 在有可用浏览器工具且用户授权后，协助微信表情开放平台上传和提交；依据实际审核反馈继续修改。

## 安装到 Codex

把此 GitHub 仓库链接发给 Codex，并说：

> 请把这个仓库安装为我的 Codex Skill。

也可以手动克隆到自己的 skills 目录：

```sh
git clone https://github.com/jianiye-coder/wechat-sticker-studio.git ~/.codex/skills/wechat-sticker-studio
```

如果设置了 `CODEX_HOME`，请使用其下的 `skills/wechat-sticker-studio` 目录。安装后若当前聊天未发现 skill，重新打开聊天或应用。

## 开始使用

上传你的照片，再发送：

> 用 $wechat-sticker-studio，根据我的照片做一套微信表情。从 brainstorm 开始，帮我生成、修改定稿，准备封面、横幅等素材，再协助上传审核。

也能从中途开始：

> 用 $wechat-sticker-studio，把我已有的表情拆成单张，检查并打包投稿素材。

> 用 $wechat-sticker-studio，保留这套的生气、疑惑和抱抱，修改其他表情。

## 环境与边界

- 生成和内容修改需要当前助手环境支持图像生成/编辑。本仓库不包含图像模型，也不附带 API 密钥。
- 附带的本地素材工具依赖 Python 3 和 Pillow；建议在项目虚拟环境安装依赖。
- 网页操作需要可用的浏览器/电脑控制工具和用户登录。扫码、实名或特定协议确认可能需要本人完成。
- 官方投稿规则可能更新。工具内参数为保守制作目标，正式投稿以当时官方页面为准。
- 不保证审核通过；保存草稿、提交审核、审核通过、上架分别记录。
- 如遇站点安全策略禁止访问，不绕过限制，改为交付完整素材供用户手动上传。
- 仓库只含通用流程与工具，不含个人照片、生成表情、登录凭据或账号资料。

官方平台：[微信表情开放平台](https://sticker.weixin.qq.com/)

## 素材工具

```sh
python scripts/prepare_assets.py --help
```

支持 `split`、`build`、`check` 三个子命令。输入清单和使用示例见 [规格与交付](references/submission.md)。图片内容仍需人工/助手视觉检查，机器校验不等于官方审核。

## 文件说明

- [SKILL.md](SKILL.md)：流程入口与行为约束。
- [references/creative.md](references/creative.md)：创意、生成与修改。
- [references/submission.md](references/submission.md)：物料规格与输入清单。
- [references/upload.md](references/upload.md)：上传、审核与失败恢复。
- [scripts/prepare_assets.py](scripts/prepare_assets.py)：本地素材处理工具。
