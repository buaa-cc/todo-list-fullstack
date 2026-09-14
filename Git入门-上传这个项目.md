# Git 入门：把这个 Todo 项目传到 GitHub

> 跟着做，每一步都写了**你该看到什么**。看到的不一样就停下来查。
> 项目路径：`D:\用户\cspractice\my-vue-app\my-vue-app`

---

## 第 0 步：装 Git（必须先做）

你机器上现在没有 Git，所有命令都会报 `git: command not found`。

**下载地址**：https://git-scm.com/download/win

国内下载慢的话用镜像：
https://registry.npmmirror.com/-/binary/git-for-windows/
（进去选最新版本的 `Git-x.xx.x-64-bit.exe`）

**安装时注意这几项，其他全部默认下一步：**

| 安装界面 | 选什么 | 为什么 |
|---|---|---|
| Default editor | 有 VS Code 就选 VS Code，否则选 Notepad | 提交时偶尔要写多行说明 |
| Adjusting your PATH | **选第二项** `Git from the command line and also from 3rd-party software` | 不选的话命令行里调不到 git |
| HTTPS transport | 保持默认 `Use the native Windows Secure Channel library` | |
| Line ending conversions | 保持默认 `Checkout Windows-style, commit Unix-style` | 项目里会混有换行符差异 |
| Credential helper | **保持默认 `Git Credential Manager`** | 后面 push 时不用每次输密码 |

装完**关掉所有终端重新开一个**（PATH 要重新加载），验证：

```bash
git --version
```

应该输出类似 `git version 2.47.1.windows.1`。

---

## 第 1 步：告诉 Git 你是谁

Git 每次提交都会记录作者。只有配置过才能提交。

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

- `--global` = 对这台机器上所有项目生效，配一次就行
- 邮箱建议用你以后注册 GitHub 的那个，这样 GitHub 能把提交关联到你的账号
- 检查一下：

```bash
git config --global --list
```

---

## 第 2 步：建仓库

先进入项目目录：

```bash
cd /d/用户/cspractice/my-vue-app/my-vue-app
```

> Git Bash 里盘符写法是 `/d/...`，不是 `D:\...`。
> 也可以直接在文件资源管理器里右键项目文件夹 → `Open Git Bash here`。

建仓库：

```bash
git init -b main
```

**你应该看到**：
```
Initialized empty Git repository in D:/用户/cspractice/my-vue-app/my-vue-app/.git/
```

**发生了什么**：目录里多了一个隐藏的 `.git` 文件夹，那就是你的版本仓库。
你的代码文件一个都没动。（`-b main` 是把默认分支名设成 `main`，和 GitHub 保持一致。
如果你的 Git 版本太老不支持，就用 `git init` 再执行 `git branch -M main`。）

现在看看 Git 眼中的状态：

```bash
git status
```

**你应该看到**一长串 `Untracked files`（未跟踪的文件）。

**注意**：列表里**不应该有** `node_modules`。你的 `.gitignore` 已经把它排除了。
如果看到了，说明 `.gitignore` 没生效，先停下来查。

---

## 第 3 步：暂存（挑出这次要提交的内容）

```bash
git add .
```

`.` 表示"当前目录下所有未被忽略的改动"。

再看一次状态：

```bash
git status
```

**变化**：刚才那些红色的 `Untracked files` 变成了绿色的 `Changes to be committed`。
这就是**暂存区**——你已经把文件"放进这次的篮子"，但还没真正存档。

**为什么要分两步（add 再 commit）？**
因为你可能改了 5 个文件，但只想把其中 3 个作为一个完整的改动提交。
暂存区就是让你能精确挑选。
不想每次都挑，`git add .` + `git commit` 连着用也行。

如果 add 多了想撤回来：

```bash
git restore --staged 文件名
```

---

## 第 4 步：提交（真正存成快照）

```bash
git commit -m "初始提交：Vue3 前端 + FastAPI 后端 + SQLite"
```

`-m` 后面是这次改动的说明（commit message）。写清楚做了什么，
以后 `git log` 才看得懂。**这一行是给未来的自己看的，别写 "update"。**

**你应该看到**：
```
[main (root-commit) a1b2c3d] 初始提交：Vue3 前端 + FastAPI 后端 + SQLite
 15 files changed, 800 insertions(+)
 create mode 100644 src/App.vue
 ...
```

到这里，**版本管理的核心已经完成了**。现在你有了第一个可以随时回退的快照。

试着改坏一个文件，然后还原：

```bash
git restore src/App.vue
```

这就是 `.bak` 文件给不了你的东西。

---

## 第 5 步：看历史

```bash
git log --oneline
```

**你应该看到**：
```
a1b2c3d (HEAD -> main) 初始提交：Vue3 前端 + FastAPI 后端 + SQLite
```

想看这次提交具体动了哪些文件：

```bash
git log --stat
```

想看某个文件改了什么：

```bash
git show src/App.vue
```

---

## 第 6 步：注册 GitHub 并建远程仓库

1. 打开 https://github.com 注册（邮箱验证）
2. 右上角 `+` → `New repository`
3. 填写：
   - **Repository name**：`todo-list-fullstack`（或你喜欢的名字）
   - **Description**：可选，随便写
   - **Public / Private**：**选 Public**（要让导师能点开看）
   - **⚠️ 下面的 `Add a README file`、`.gitignore`、`license` 全部不要勾**
4. 点 `Create repository`

**为什么都不勾？** 勾了的话 GitHub 会先给你生成一个提交，
你本地也有提交，两边历史不一样，push 时会冲突报错。
让远程仓库**保持完全空**，push 最顺。

创建后你会看到一个空仓库页面，里面有 `https://github.com/你的用户名/todo-list-fullstack.git`
这个地址——**记下来，下一步要用**。

---

## 第 7 步：把本地仓库和远程仓库关联

```bash
git remote add origin https://github.com/你的用户名/todo-list-fullstack.git
```

- `remote` = 远程仓库
- `origin` = 给这个远程仓库起的别名（习惯叫 origin，你也可以起别的）
- 一个本地仓库可以关联多个远程（比如同时关联 GitHub 和 Gitee）

检查：

```bash
git remote -v
```

**应该看到**两行（fetch 和 push）。

---

## 第 8 步：推上去

```bash
git push -u origin main
```

- `push` = 把本地提交上传到远程
- `-u` = 记住这次的关联，以后直接 `git push` 就行，不用再写参数

**第一次会弹出一个窗口让你登录 GitHub**（这就是刚才装的 Credential Manager 在干活）。
选 `Sign in with your browser`，浏览器里授权一下。**只需授权一次**，以后不再问。

**你应该看到**：
```
Enumerating objects: 20, done.
Writing objects: 100% (20/20), 15.2 KiB | 2.5 MiB/s, done.
To https://github.com/你的用户名/todo-list-fullstack.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

刷新 GitHub 页面，你的文件就在上面了。

---

## 第 9 步：验证

本地和远程是否一致：

```bash
git status
```

**应该看到** `Your branch is up to date with 'origin/main'.` 和 `nothing to commit, working tree clean`。

---

## 以后的日常流程（只需记这四条）

```bash
git status              # 1. 看看改了什么
git add .               # 2. 全部放进暂存区
git commit -m "说明"     # 3. 存一个快照
git push                # 4. 传到 GitHub
```

改一次代码走一遍这四步。**commit 是本地操作，不联网；push 才联网。**

---

## 常见报错

| 报错 | 原因 | 解决 |
|---|---|---|
| `git: command not found` | Git 没装，或装了没重启终端 | 装 Git / 重启终端 |
| `Please tell me who you are` | 没配 user.name/email | 回到第 1 步 |
| `src refspec main does not match any` | 还没 commit，或分支名是 master | 先 commit；或 `git branch -M main` |
| `rejected ... fetch first` | 远程仓库里有你本地没有的提交（通常建仓库时勾了 README） | 删掉 GitHub 仓库重建，或 `git pull --rebase origin main` |
| `Failed to connect to github.com` | 网络问题（国内常见） | 看下面「连不上 GitHub 怎么办」 |
| `Support for password authentication was removed` | 输密码而不是用浏览器登录 | 删掉凭证重试：控制面板 → 凭据管理器 → 删除 github.com 相关项 |
| 提示某个文件太大 | 通常是把 `node_modules` 提交了 | `git rm -r --cached node_modules` 后重新提交 |

---

## 连不上 GitHub 怎么办

国内访问 GitHub 的 push 经常超时。三个办法，从易到难：

1. **换 Gitee（码云）** —— 最省事。注册 gitee.com，流程完全一样，
   只是仓库地址变成 `https://gitee.com/你的用户名/todo-list-fullstack.git`。
   **简历上写 Gitee 链接完全可以**，能打开才是重点。
2. **两个都推**（推荐）：
   ```bash
   git remote add gitee https://gitee.com/你的用户名/todo-list-fullstack.git
   git push gitee main
   ```
   以后 `git push` 推 GitHub，`git push gitee` 推码云。
3. 配置代理（需要你自己有代理工具，这里不展开）。

---

## 命令速查

| 命令 | 作用 |
|---|---|
| `git status` | 当前状态（最常用，随时敲） |
| `git add .` | 全部改动放入暂存区 |
| `git add 文件名` | 只暂存指定文件 |
| `git commit -m "说明"` | 存一个快照 |
| `git log --oneline` | 看历史（一行一条） |
| `git log --stat` | 看历史 + 每次动了哪些文件 |
| `git diff` | 看还没暂存的改动内容 |
| `git diff --staged` | 看已暂存待提交的改动内容 |
| `git restore 文件名` | 丢弃某个文件的改动（**谨慎，不可恢复**） |
| `git restore --staged 文件名` | 把它移出暂存区（改动保留） |
| `git push` | 上传到远程 |
| `git pull` | 拉取远程改动 |
| `git remote -v` | 看关联了哪些远程仓库 |

---

## 最后两件事

1. **先加一行 `*.bak` 到 `.gitignore`，再执行第一次 commit。**

   我实际预览过：目前 `git add .` 会跟踪 **22 个文件**，其中包含 `src/App.vue.bak`。
   在第一次 commit 之前把它排除掉，它就不会进入版本历史：

   ```bash
   echo "*.bak" >> .gitignore
   ```

   这样文件数变成 21 个。等 Git 跑通后，`App.vue.bak` 就可以直接删了 ——
   Git 本身就是备份，`.bak` 留在仓库里只是垃圾。

   （另外 `src/components/` 是个空目录，Git 不跟踪空目录，所以它不会出现在
   文件列表里，这是正常现象。）

2. **别忘了把 GitHub 链接写进简历**。这才是这个项目真正的用途：
   ```
   https://github.com/你的用户名/todo-list-fullstack
   ```
   导师点开能看到代码、能看提交时间分布——这是你简历上唯一"可被验证"的东西。
