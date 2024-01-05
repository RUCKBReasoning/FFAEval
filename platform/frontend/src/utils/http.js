import axios from 'axios'

// 创建一个新的axios对象
let instance = axios.create({
  timeout: 60000,
  baseURL: import.meta.env.VITE_BASE_URL,
})

// 设置请求拦截器
instance.interceptors.request.use(
  function (config) {
    return config
  },
  function (error) {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  function (response) {
    return response
  },
  function (error) {
    return Promise.reject(error)
  }
)

// 暴露 axios 实例
export default instance