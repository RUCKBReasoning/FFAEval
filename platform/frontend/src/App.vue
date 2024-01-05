<script>
import ChatRoom from './components/ChatRoom.vue'

export default {
  name: "App",
  components: { ChatRoom }
}
</script>

<template>
  <div>
    <ChatRoom/>
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
}

@font-face {
  font-family: "Arial";
  src: local("Arial"), url(assets/fonts/ARIAL.TTF) format("truetype");
}

/* .el-input__wrapper {
  border-radius: 19px;
} */
</style>
