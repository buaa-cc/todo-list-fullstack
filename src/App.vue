<script setup>
import { onMounted, ref } from 'vue'

// 后端地址。启动后端后它就是 http://127.0.0.1:8000
const API_BASE = 'http://127.0.0.1:8000'

const inputValue = ref('') // 输入框的值
const list = ref([])       // 任务列表，改为从后端拉取，初始为空
const loading = ref(false) // 是否正在加载
const error = ref('')      // 错误提示

/**
 * 统一封装请求：省掉每个函数里重复的 fetch 配置和错误判断。
 * 204 是 DELETE 成功时的状态码，没有响应体，不能调用 res.json()。
 */
async function request(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`${options.method || 'GET'} ${path} → HTTP ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}

/** 读取列表：GET /todos */
async function load() {
  loading.value = true
  error.value = ''
  try {
    list.value = await request('/todos')
  } catch (e) {
    error.value = `读取列表失败：${e.message}（后端启动了吗？）`
  } finally {
    loading.value = false
  }
}

/** 新增：POST /todos */
async function add() {
  const text = inputValue.value.trim()
  if (!text) return // 空内容不提交
  error.value = ''
  try {
    const created = await request('/todos', {
      method: 'POST',
      body: JSON.stringify({ text }),
    })
    // 后端按创建时间倒序返回，新增的放最前面，保持一致
    list.value.unshift(created)
    inputValue.value = ''
  } catch (e) {
    error.value = `新增失败：${e.message}`
  }
}

/** 勾选完成：PATCH /todos/{id} */
async function toggle(item) {
  error.value = ''
  try {
    const updated = await request(`/todos/${item.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ done: !item.done }),
    })
    // 用后端返回的最新数据覆盖本地对象，保证前后端一致
    Object.assign(item, updated)
  } catch (e) {
    error.value = `更新失败：${e.message}`
  }
}

/** 删除：DELETE /todos/{id} */
async function del(item) {
  error.value = ''
  try {
    await request(`/todos/${item.id}`, { method: 'DELETE' })
    list.value = list.value.filter((t) => t.id !== item.id)
  } catch (e) {
    error.value = `删除失败：${e.message}`
  }
}

// 组件挂载后立即拉一次列表 —— 这一步让数据"活"起来了
onMounted(load)
</script>

<template>
  <div class="todo-app">
    <div class="title">Todo App</div>

    <div class="todo-form">
      <input
        v-model="inputValue"
        type="text"
        class="todo-input"
        placeholder="Add a todo"
        @keyup.enter="add"
      />
      <div @click="add" class="todo-button">Add Todo</div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading" class="hint">加载中…</div>
    <div v-else-if="list.length === 0" class="hint">还没有任务，添加一条试试</div>

    <div
      v-for="item in list"
      :key="item.id"
      :class="[item.done ? 'completed' : 'item']"
    >
      <div>
        <input type="checkbox" :checked="item.done" @change="toggle(item)" />
        <span class="name">{{ item.text }}</span>
      </div>

      <div @click="del(item)" class="del">del</div>
    </div>
  </div>
</template>

<style scoped>
.todo-app {
  box-sizing: border-box;
  margin-top: 40px;
  margin-left: 1%;
  padding-top: 30px;
  width: 98%;
  min-height: 500px;
  background: #ffffff;
  border-radius: 5px;
}

.title {
  text-align: center;
  font-size: 30px;
  font-weight: 700;
}

.todo-form {
  display: flex;
  margin: 20px 0 30px 20px;
}

.todo-button {
  width: 100px;
  height: 52px;
  border-radius: 0 20px 20px 0;

  text-align: center;
  background: linear-gradient(
    to right,
    rgb(113, 65, 168),
    rgba(44, 114, 251, 1)
  );
  color: #fff;
  line-height: 52px;
  cursor: pointer;
  font-size: 14px;
  user-select: none;
}

.todo-input {
  padding: 0px 15px 0px 15px;
  border-radius: 20px 0 0 20px;
  border: 1px solid #dfe1e5;
  outline: none;
  width: 60%;
  height: 50px;
}

.item {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 80%;
  height: 50px;
  margin: 8px auto;
  padding: 16px;
  border-radius: 20px;
  box-shadow: rgba(149, 157, 165, 0.2) 0px 8px 20px;
}

.del {
  color: red;
  cursor: pointer;
}

.completed {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 80%;
  height: 50px;
  margin: 8px auto;
  padding: 16px;
  border-radius: 20px;
  box-shadow: rgba(149, 157, 165, 0.2) 0px 8px 20px;
  text-decoration: line-through;
  opacity: 0.4;
}

.error {
  width: 80%;
  margin: 0 auto 12px;
  padding: 10px 16px;
  border-radius: 10px;
  background: #fdecec;
  color: #b42318;
  font-size: 14px;
}

.hint {
  width: 80%;
  margin: 0 auto;
  color: #8a94a0;
  font-size: 14px;
}
</style>
