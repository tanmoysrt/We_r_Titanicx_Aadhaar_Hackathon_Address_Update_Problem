<template>
  <header>
    <div class="logos">
      <div class="uidai-logo">
        <img src="/img/uidai logo.png" />
      </div>
      <div class="aadhar-logo">
        <img src="/img/aadhar logo.png" />
      </div>
    </div>
    <div class="heading">
      <h1>Aadhar address Updation</h1>
    </div>
  </header>

  <main>
    <router-view
      v-if="status == 0"
      :notification_redirection_decision="notification_redirection_decision"
    />
    <div class="success-failed" v-else-if="status == 1">
      <img src="/img/success.png" />
      <h3>{{ message }}</h3>
    </div>
    <div class="success-failed" v-else-if="status == 2">
      <img src="/img/success.png" />
      <h3>{{ error }}</h3>
    </div>
  </main>
</template>

<script>
export default {
  data(){
    return {
      status: 0,
      /* 
        Status -> 0 -> no error , show router view
        -> 1 -> Successful page
        -> 2 -> Error page
      */
      message: "",
      error: "",
    }
  },
  methods: {
    show_page(is_success, message){
      if(is_success){
        this.status = 1;
        this.message = message;
      }else{
        this.status = 2;
        this.error = message;
      }
    },
    notification_redirection_decision(payload){
      console.log(payload);
      // this.status = 1;

      // Payload contains a success , error. message
      if (payload["success"]) {
        this.message = payload["message"];
        if (payload["page_show"]) {
          this.status = 1;
        } else {
          this.$toast.open({
            message: payload["message"],
            type: "success",
            duration: 2000,
            dismissible: true
          })
        }
      } else {
        this.error = payload["error"];
        if (payload["page_show"]) {
          this.status = 2;
        } else {
          this.$toast.open({
            message: payload["error"],
            type: "error",
            duration: 2000,
            dismissible: true
          })
        }
      }
    }
  }
}
</script>
