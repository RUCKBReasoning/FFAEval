<script>
import { nextTick } from 'vue'
import http from '../utils/http.js'
import makeid from '../utils/tool.js'
import { SwitchButton, RefreshRight } from '@element-plus/icons-vue'
import io from 'socket.io-client'

export default {
  data() {
    return {
      sessionId: '',
      isPhone: false,

      msgList: [],
      msg: '',          // the message in the input box
      isAppend: false,     // whether current message is needed to append
      chatContext: [],  // current conversation context
      choosen_num: 0,

      botList: [],
      rankList: [],     // learderboard
      botOrder: [],     // the real chatbot order

      state: 0,
      placeholder: 'Say something',
  
      inputDisabled: false,
      regenerateDisabled: true,
      restartDisabled: true,
      terminateDisabled: true,

      rankVisible: false,
    }
  },

  created() {
    if (window.navigator.userAgent.match(/(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)/i))
      this.isPhone = true
  },

  mounted() {
    http.post('/backend/bot').then(res => {
      this.botList = res.data.bot_list
    })
    this.sessionId = makeid(10)
  },

  watch: {
    state (newData, oldData) {
      switch (newData) {
        case 0:
          this.placeholder = 'Please reply to the selected bubbles'
          this.inputDisabled = false
          this.regenerateDisabled = false
          break
        case 1:
          this.placeholder = "Wait for chatbot's reply"
          this.inputDisabled = true
          this.regenerateDisabled = true
          this.terminateDisabled = true
          break
        case 2:
          this.placeholder = "Please click one of the messages you'd like to talk to"
          this.inputDisabled = true
          this.regenerateDisabled = false
          this.terminateDisabled = false
          break
        case 3:
          this.placeholder = 'Click restart to start a new conversation'
          this.inputDisabled = true
          this.regenerateDisabled = true
          this.terminateDisabled = true
          this.restartDisabled = false
          break
      }
    }
  },

  methods: {
    clickEnter(e) {
      if (e.keyCode == 13)
        this.sendMsg()
    },
  
    async addMsg(msg, isAppend) {
      if (!isAppend) {
        if (msg.direction == 'left') {
          let botMsg = {'direction': 'left', 'contentList': []}
          for (let m of msg.contentList) {
            botMsg.contentList.push({'content': m + '▌', 'chosen': false})
          }
          this.msgList.push(botMsg)
        } else {
          this.msgList.push(msg)
        }
      } else {
        for (let i = 0; i < msg.contentList.length; i++) {
          this.msgList[this.msgList.length - 1]['contentList'][i]['content'] = 
            this.msgList[this.msgList.length - 1]['contentList'][i]['content'].slice(0, -1)
          this.msgList[this.msgList.length - 1]['contentList'][i]['content'] += msg.contentList[i]
          this.msgList[this.msgList.length - 1]['contentList'][i]['content'] += '▌'
        }
      }
      // await nextTick()
      nextTick(() => {
        this.$refs.scrollbarRef.setScrollTop(this.$refs.innerRef.clientHeight)
      })
    },
  
    websocket(data) {
      var socket = io('http://IP_ADDRESS:PORT/chat', {transports: ['polling']});

      // establish websocket connection
      socket.on('connect', () => {
        console.log('sucessfully connect to WebSocket server');

        // send message to server
        socket.emit('message', data);

        // listen to the server's response
        socket.on('message', (msg) => {
          if (msg.state == 'unfinished') {
            this.addMsg({'direction': 'left', 'contentList': msg.msg_list}, this.isAppend)
            this.isAppend = true
          } else {
            this.state = 2
            this.choosen_num = 0

            for (let i = 0; i < this.botList.length; i++)
              this.msgList[this.msgList.length - 1]['contentList'][i]['content'] = this.msgList[this.msgList.length - 1]['contentList'][i]['content'].slice(0, -1)
            socket.disconnect();
            console.log('close connection to WebSocket server');
          }
        });
      });

      // Listen for connection disconnection events
      socket.on('disconnect', function() {
        console.log('Successfully disconnected');
      });
    },

    async sendMsg() {
      if (this.msg == '')
        return
      this.addMsg({direction: 'right', content: this.msg}, false)
      this.chatContext.push(this.msg)  // add message to history context
      this.msg = ''
      this.state = 1
      this.isAppend = false

      // send message to backend
      const data = {
        'session_id': this.sessionId,
        'msg_send': this.chatContext,
        'regenerate': false
      }

      this.websocket(data)

    },

    clickBubble(i, j) {
      if ((this.state == 0 || this.state == 2) && i + 1 == this.msgList.length) {
        for (let k = 0; k < this.msgList[i].contentList.length; k++)
          this.msgList[i].contentList[k].chosen = false
        this.msgList[i].contentList[j].chosen = true
        if (this.state == 2) {
          this.state = 0
          this.chatContext.push(this.msgList[i].contentList[j].content)
        } else {
          this.chatContext[this.chatContext.length - 1] = this.msgList[i].contentList[j].content
        }
        // Update selected information in the database
        const data = {
          'session_id': this.sessionId,
          'chosen_msg_index': j
        }
        http.post("/backend/choose", data)
      }
    },

    closeRank() {
      this.rankVisible = false
      if (this.botOrder.length != 0)
        this.popMessage('info', 'Click restart to start a new conversation')
    },

    popMessage(type, msg) {
      ElMessage({
        type: type,
        message: msg,
        duration: 4000,
      })
    },

    async regenerate() {
      if (this.msgList.length == 0)
        return
      if (this.state == 1) {
        this.popMessage('warning', 'please wait for the reply to be generated before regenerating')
        return
      }
      if (this.state == 0)
        this.chatContext.pop()
      this.state = 1
      this.msgList.pop()

      this.isAppend = false

      // Send messages to the backend
      const data = {
        'session_id': this.sessionId,
        'msg_send': this.chatContext,
        'regenerate': true
      }

      this.websocket(data)

    },

    terminate() {
      if (this.msgList.length != 0) {
        const data = {
          'session_id': this.sessionId
        }
        http.post("/backend/terminate", data).then(res => {
          this.rankList = res.data.rank_list
          this.rankVisible = true
          this.botOrder = res.data.order_list
          this.state = 3

          this.popMessage('success', 'Successfully ended conversation')
        })
      }
    },

    restart() {
      this.sessionId = makeid(10)
      this.msg = ''
      this.msgList = []
      this.state = 0
      this.chatContext = []
      this.placeholder = 'Say something'
      this.botOrder = []
      this.inputDisabled = false
      this.regenerateDisabled = true
      this.restartDisabled = true
      this.terminateDisabled = true
    },
  },
  components: {
    SwitchButton, RefreshRight
  }
}
</script>

<template>
  <div class="container">
    <div class="title">FFAEval: Evaluating Dialogue System via Free-For-All Ranking</div>
    <div class="subtitle">Rules</div>
    <li class="text">Chat with multiple chatbots simultanously in this platform.</li>
    <li class="text">After each robot's message is generated, you have to choose the message you would like to talk with in next turn by clicking one of the message bubbles.</li>
    <li class="text">All chatbots are anonymous. If you no longer want to chat, you can click "Terminate and Restart," and the ranking list of the current conversation will be revealed.</li>
    <li class="text">When the conversation ends, we calculate the ranking based on the number of times the chatbot has been selected. Frequently selected chatbots rank higher.</li>
    <li class="text">The leaderboard will be calculated using the ranking of each conversation and the TrueSkill algorithm.</li>
    <div class="subtitle">Online Chatbot</div>

    <el-row class="text">
      <div v-for="(bot, i) in botList" :key="i">
        <el-col :span="50" style="margin-right: 10px">{{ i }}) {{ bot }}</el-col>
      </div>
    </el-row>

    <div class="main" :style="isPhone ? 'height: calc(100vh - 64px - 40px)' : 'height: calc(100vh)'">
      <el-scrollbar ref="scrollbarRef">
        <div ref="innerRef">
          <div v-for="(msg, i) in msgList" :key="i">
            <div v-if="msg.direction=='right'" class="bubble right" style="margin-top: 15px">
              <span class="bubble-right">
                <div class="msg right">{{ msg.content }}</div>
              </span>
              <img class="avatar right" src="../assets/images/user.png"/>
            </div>
            <div v-else class="bubble-whole" style="margin-top: 15px; margin-bottom: 15px;">
              <div v-for="(content, j) in msg.contentList" :key="j" class="bubble left" @click="clickBubble(i, j)">
                <div class="avatar left" :style="content.chosen ? 'background-color: #01B99B; color: #fff' : ''">
                  {{ botOrder.length > 0 ? botOrder[parseInt(i / 2)][j] : String.fromCharCode(65 + j) }}
                </div>
                <span class="bubble-left" :style="content.chosen ? 'background-color: #01B99B;' : ''">
                  <div id='left-msg' class="msg left" :style="content.chosen ? 'color: #fff' : ''">
                    {{ content.content }}</div>
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>

    <!-- input line -->
    <div class="send">
      <el-input v-model="msg" :placeholder="placeholder" style="margin-right: 10px;" size="large"
        @keydown.enter.native="clickEnter" :disabled="inputDisabled">
      </el-input>
      <el-button type="primary" size="large" @click="sendMsg" :disabled="inputDisabled" circle>
        <template #icon>
          <el-icon :size="23"><Promotion /></el-icon>
        </template>
      </el-button>
    </div>

    <!-- buttons -->
    <div class="buttons">
      <el-button class="operate" size="large" @click="regenerate" :disabled="regenerateDisabled">
        <el-icon style="vertical-align: middle;">
          <RefreshRight />
        </el-icon>
        <span style="vertical-align: middle;">Regenerate</span>
      </el-button>

      <el-button class="operate" size="large" @click="terminate" :disabled="terminateDisabled">
        <el-icon style="vertical-align: middle;">
          <SwitchButton />
        </el-icon>
        <span style="vertical-align: middle;">Terminate</span>
      </el-button>

      <el-button class="operate" size="large" @click="restart" :disabled="restartDisabled">
        <el-icon style="vertical-align: middle;">
          <RefreshRight />
        </el-icon>
        <span style="vertical-align: middle;">Restart</span>
      </el-button>
    </div>

    <!-- rank list -->
    <el-dialog v-model="rankVisible" title="Ranking of The Last Chat" :width="isPhone ? '90%' : '60%'" @closed="closeRank" center>
      <el-table :data="rankList" :stripe="true">
        <el-table-column type="index" width="50" />
        <el-table-column align="center" property="bot_name" label="Name of Chatbot"/>
        <el-table-column align="center" property="chosen_num" label="Number of Selected Times"/>
      </el-table>
    </el-dialog>

  </div>
</template>

<style scoped>
div span li {
  font-family: "Arial";
  /* color: #2D2D2D; */
}

/* Mobile */
@media (max-width: 675px) {
  .container {
    /* width: 100%;
    height: calc(100vh); */
    margin: 20px 5px;
    width: 100%;
    display: flex;
    flex-direction: column;
  }
}

/* PC */
@media (min-width: 675px) {
  .container {
    margin: 20px calc(17vh);
    display: flex;
    flex-direction: column;
  }
}

.title {
  font-size: 26px;
  font-weight: bold;
  margin: 8px 0;
}

.subtitle {
  font-size: 16px;
  font-weight: bold;
  margin: 8px 0;
}

.text {
  font-size: 14px;
  margin: 4px 0;
}

.main {
  width: 100%;
  min-height: 550px;
  max-height: 550px;
  border: 1px solid rgb(224, 224, 224);
  border-radius: 8px;
  overflow-x: hidden;
  overflow-y: auto;
  margin-top: 15px;
}

.send {
  display: flex;
  margin: 15px 0;
}

.buttons {
  display: flex;
}

.operate {
  width: 100%
}

.bubble {
  margin: 10px 0px;
  border-width: 0 12px;
  display: -webkit-flex;
  display: flex;
  -webkit-align-items: top;
  align-items: top;
}
.bubble.left {
  margin-left: 12px;
}
.bubble.right {
  -webkit-justify-content: flex-end;
  justify-content: flex-end;
  margin-right: 12px;
}

/* Mobile */
@media (max-width: 675px) {
  .bubble-left {
    width: calc(80%);
    padding: 5px 7px;
    margin-left: 10px;
    border-radius: 5px;
    background-color: #fff;
  }
}

/* PC */
@media (min-width: 675px) {
  .bubble-left {
    width: calc(93%);
    padding: 5px 7px;
    margin-left: 10px;
    border-radius: 5px;
    background-color: #fff;
  }
}

.bubble-right {
  padding: 5px 7px;
  margin-right: 10px;
  border-radius: 9px 9px 0px 9px;
  background-color: #088AF2;
}
.bubble-whole {
  margin: 0 40px 0 12px;
  padding: 5px 0;
  border-radius: 9px 9px 9px 0px;
  background-color: #F7F7F7;
}

.avatar {
  border-radius: 20px;
  box-shadow: 1px 2px 4px 0px rgb(185, 185, 185);
  z-index: 1;
}

.avatar.left {
  display: inline-block;
  text-align: center;
  height: 30px;
  width: 30px;
  line-height: 30px;
  font-size: 16px;
  color: #2D2D2D;
  position: relative;
  top: 4px;
}
.avatar.right {
  height: 30px;
  width: 30px;
}
.msg {
  font-size: 15px;
  line-height: 32px;
}
.msg.left {
  color: #2D2D2D;
  white-space: pre-line;
  padding: 0 5px;
}
.msg.right {
  max-width: calc(100vw - 72px - 50px);
  color: #fff;
  position: relative;
  left: 1px;
  padding: 0 5px;
}
</style>
