# App.vue 语法拆解 —— 哪块是 HTML、哪块是 CSS、哪块是 JavaScript

> 结论先给：**`.vue` 文件里没有"Vue 语言"。** 它是一份**单文件组件（SFC, Single File Component）**，
> 把三种你本来就认识的语言装进一个文件，用三个顶层标签隔开。
> "用 Vue 写的"这个说法要改一改：**Vue 不是语言，是 JavaScript 框架**。
> 所谓用 Vue 写，指的是「用 JavaScript 调 Vue 的函数」+「在 HTML 里用 Vue 的指令」。

---

## 一、三个块，一眼看懂

| 块 | 行号（本文件） | 真实语言 | Vue 额外加了什么 |
|---|---|---|---|
| `<script setup>` | 1–87 | **JavaScript** | `ref()`、`.value`、`onMounted()` |
| `<template>` | 89–121 | **HTML** | `{{ }}`、`v-if`、`v-for`、`:class`、`@click` |
| `<style scoped>` | 123–222 | **CSS** | 只有 `scoped` 这一个属性 |

判断口诀（看任何 `.vue` 文件都适用）：

- 在 `<template>` 里 → HTML + Vue 指令
- 在 `<style>` 里 → CSS
- 在 `<script>` 里 → JavaScript

---

## 二、`<script setup>`（第 1–87 行）—— JavaScript 是主角

### 这些是纯 JavaScript，和 Vue 完全无关

| 行号 | 代码 | 是什么 |
|---|---|---|
| 5 | `const API_BASE = '...'` | 变量声明 |
| 16 | `async function request(path, options = {})` | 异步函数 + 参数默认值 |
| 17 | `await fetch(...)` | 发网络请求（浏览器内置 API） |
| 19 | `...options` | 展开运算符 |
| 21–23 | `if (!res.ok) throw new Error(...)` | 条件判断 + 抛异常 |
| 22 | `` `${options.method \|\| 'GET'} ...` `` | 模板字符串 + 逻辑或 |
| 32–38 | `try / catch / finally` | 异常处理 |
| 43 | `inputValue.value.trim()` | 字符串方法 |
| 52 | `list.value.unshift(created)` | 数组方法（头部插入） |
| 68 | `Object.assign(item, updated)` | 对象方法 |
| 79 | `(t) => t.id !== item.id` | 箭头函数 |
| 79 | `.filter(...)` | 数组方法（筛选） |

**这部分你已经在 CS61A 里练过同类的了**，语法只是从 Python 换成 JavaScript，思路一样：
定义变量 → 定义函数 → 调函数 → 处理错误。

### 这些是 Vue 特有的，只有三样

| 行号 | 代码 | 作用 |
|---|---|---|
| 7–10 | `const list = ref([])` | 把普通值变成**响应式**：值一变，页面自动更新 |
| 30、33 | `loading.value = true` | 读写 ref 变量**必须加 `.value`** |
| 86 | `onMounted(load)` | 生命周期钩子：组件渲染出来后执行 `load` |
| 1 | `setup` 这个后缀 | 表示"本作用域里定义的东西，模板可以直接用" |

`.value` 是新手最容易忘的一处：**`ref` 包起来的变量不是它本身，是个"盒子"，
`.value` 才是盒子里的东西**。在 `<script>` 里读写都要加，在 `<template>` 里不用加
（Vue 自动帮你剥了一层）。

---

## 三、`<template>`（第 89–121 行）—— HTML 为主，Vue 指令是插件

### 纯 HTML 的部分

`<div>`、`<input>`、`<span>`、`class="..."`、`type="text"`、`placeholder="..."`、`<br>` 换行结构……
这些和你在记事本里写的静态网页没区别。

### Vue 加进来的（HTML 本身没有这些）

| 写法 | 行号 | 名字 | 含义 |
|---|---|---|---|
| `{{ error }}` | 104 | 插值 | 把 JS 里的值输出到页面上 |
| `v-model="inputValue"` | 95 | 双向绑定 | 输入框 ↔ 变量，改哪边另一边都跟着变 |
| `v-if="error"` | 104 | 条件渲染 | 条件不成立就**不渲染这个元素** |
| `v-else-if="..."` | 106 | 条件渲染 | 接在上一个 `v-if` 后面 |
| `v-for="item in list"` | 109 | 列表渲染 | 按数组长度重复生成 DOM |
| `:key="item.id"` | 110 | 唯一标识 | 帮 Vue 判断哪个元素是哪个，列表必备 |
| `:class="[...]"` | 111 | 动态属性 | 属性值用 **JS 表达式**，不是固定字符串 |
| `:checked="item.done"` | 114 | 动态属性 | 复选框是否勾上 |
| `@click="add"` | 101、118 | 事件绑定 | 点击时执行 `add` 函数 |
| `@change="toggle(item)"` | 114 | 事件绑定 | 勾选变化时执行 |
| `@keyup.enter="add"` | 99 | 事件修饰符 | 回车键抬起时才触发 |

### 四个符号的记忆法

```
{{ }}     →  把 JS 的值塞进 HTML
v-xxx     →  指令（v-if / v-for / v-model / v-show）
:属性     →  v-bind 的简写，属性值当 JS 表达式算
@事件     →  v-on 的简写，绑定事件处理函数
```

`:class` 和 `class` 的区别最容易搞混：
- `class="todo-app"` → 永远是 `todo-app` 这个类名
- `:class="[item.done ? 'completed' : 'item']"` → 是 JS，运行后才知道用哪个类名

---

## 四、`<style scoped>`（第 123–222 行）—— 纯 CSS，一行 Vue 都没有

`.todo-app { ... }`、`.title { ... }`、`display: flex`、`border-radius` —— 全是标准 CSS。

唯一的 Vue 痕迹是 **`scoped`** 这个词：
- 不加 `scoped`：这些样式是**全局的**，会影响整个页面的所有组件
- 加了 `scoped`：Vue 编译时给每个元素加一个随机属性（如 `data-v-7ba5bd90`），
  样式选择器也跟着改，于是**只对本组件生效**

这是 Vue 很实用的一个设计：一个项目的样式分散在几十个组件里，
没有 `scoped` 的话类名冲突会让人崩溃。

---

## 五、三个块是怎么连起来的（这才是 Vue 的核心）

`<script>` 里定义的变量和函数，`<template>` 里直接用名字引用：

| script 里定义 | template 里使用 | 关系 |
|---|---|---|
| `inputValue`（第 7 行） | `v-model="inputValue"`（第 95 行） | 输入框的值存进这个变量 |
| `add`（第 42 行） | `@click="add"`（第 101 行） | 点按钮就调这个函数 |
| `list`（第 8 行） | `v-for="item in list"`（第 109 行） | 数组有几条就渲染几个 div |
| `item.text`（后端数据） | `{{ item.text }}`（第 115 行） | 显示任务内容 |
| `error`（第 10 行） | `v-if="error"`（第 104 行）+ `{{ error }}` | 有错误才显示红条 |
| `loading`（第 9 行） | `v-if="loading"`（第 105 行） | 加载时才显示提示 |

**关键区别（和你以前写原生 JS 的差别）**：
以前你要手动操作 DOM —— `document.querySelector('.list').innerHTML = ...`。
现在你只改数据 —— `list.value = [...]`，**Vue 自己算出该改哪些 DOM**。
这叫"数据驱动视图"，是 Vue/React 这类框架存在的理由。

---

## 六、为什么 `.vue` 能跑起来？浏览器其实不认识它

浏览器只会解析三种东西：**HTML、CSS、JavaScript**。它不认识 `.vue`。

`.vue` 是给开发者用的"容器"，打包工具负责拆开：

```
       App.vue（开发者写的）
              │
        Vite + @vitejs/plugin-vue   ← 构建时编译
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
HTML 结构   JavaScript   CSS
（render    （script      （style
 函数）      原样保留）     加 scoped 属性）
```

所以 `npm run build` 之后，`dist/` 目录里只有 `.html` / `.css` / `.js`，
**一个 `.vue` 文件都没有** —— 它们全被编译掉了。

也可以说：`.vue` 是一种"编译期语法"，只存在于你的源码里。

---

## 七、你可能会问的几个问题

**Q：那我是先学 HTML/CSS/JS 还是先学 Vue？**
先学前三个。Vue 只在它们之上加了一层薄薄的语法，底层不会的话，Vue 的报错你读不懂。

**Q：`<script setup>` 里的 `import { ref } from 'vue'` 是什么？**
JavaScript 的模块导入语法（ES Module）。和 Python 的 `from vue import ref` 一个意思。
`'vue'` 是 `node_modules` 里的包名。

**Q：为什么两个 `<script>` 标签的写法我没有？**
老写法是 `<script>` + `export default { data() {...}, methods: {...} }`。
`<script setup>` 是 Vue 3.2+ 的新语法，代码更短，现在推荐用它。

**Q：`del` 这个函数名不是 JavaScript 关键字吗？**
不是。JS 保留字里没有 `del`（Python 才有 `del`）。这里只是个普通函数名。

**Q：三个块的顺序能换吗？**
能。习惯上把 `<template>` 放最前面（先看结构）、`<script>` 次之、`<style>` 最后。
本文件是 script 在前，也没问题。
