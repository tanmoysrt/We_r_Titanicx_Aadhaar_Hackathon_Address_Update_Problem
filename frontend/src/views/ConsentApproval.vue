<template>
  <div v-if="step == 1">
    <form>
      <div class="input-field aadhar-field">
        <label for="">Enter your 12 digit Aadhar number</label>
        <input type="number" maxlength="12" v-model="uid" :disabled="iscaptchaverified" />
      </div>
      <div class="row">
        <div class="captcha"><img :src="captchaBase64" /></div>
        <div class="input-field">
          <label for="">Enter the Captcha</label>
          <input type="text" v-model="captchaValue" :disabled="iscaptchaverified"  />
        </div>
      </div>
      <button v-on:click.stop.prevent="verifyCaptchaAndSendOTP"  class="btn-primary login-btn">Generate OTP</button>
    </form>

    <form>
      <div class="row">
        <div class="input-field">
          <label for="">Enter OTP</label>
          <input type="number" maxlength="8" v-model="otp"  :disabled="iscaptchaverified==false"  />
        </div>
        <div class="otp-verify"><button class=" btn-primary" v-on:click.stop.prevent="verifyOTP">Verify OTP</button></div>
      </div>
    </form>
  </div>

  <div v-if="step == 2">
    <p><b>Please verify all details before accepting the consent for aadhaar update request</b></p>
    <div class="renter-deatils">
        <div class="photo-field grid-field">
            <p><b>Photo</b></p>
             <img :src="user.photo" >
        </div>
        <div class="name-field grid-field">
            <p><b>Name</b></p>
            <p>{{ user.name }}</p>
        </div>
        <div class="address-field grid-field">
            <p><b>Contact</b></p>
            <p>{{ user.mobile_no }}</p>
        </div>
    </div>
      <div class="btn-row">
          <button class=" btn-primary btn-green" v-on:click.stop.prevent="submitDecision('y')">APPROVE</button>
          <button class=" btn-primary btn-red"  v-on:click.stop.prevent="submitDecision('n')">REJCT</button>
      </div>
  </div>
</template>

<script>
import helper from "../helper_functions";

async function getCaptcha(){
  var responseCaptcha = await helper.REST_API(()=>{},{}, "/request/captcha/", "", false, "get", true);
  if (responseCaptcha["success"]) {
    console.log(responseCaptcha);
    return responseCaptcha["payload"];
    // captchaTxnId = responseCaptcha["captchaTxnId"];
    // captchaBase64 = "data:image/jpeg;base64,/" + responseCaptcha["captchaBase64String"];
  }
  return "-1";
}

export default {
  name: "Approve Consent",
  components: {},
  async mounted() {
    var data = await getCaptcha();
    this.captchaTxnId = data["captchaTxnId"];
    this.captchaBase64 = "data:image/jpeg;base64," + data["captchaBase64String"];
  },
  props: ["notification_redirection_decision"],
  data() {
    return {
      step: 1,
      iscaptchaverified: false,
      uid: "",
      captchaValue: "",
      captchaTxnId: "",
      captchaBase64: "data:image/jpeg;base64,/",
      otp_transaction_id: "",
      request_transaction_id: "",
      otp: "",
      jwt_token: "",
      request_status: "",
      user: {
        name: "",
        photo: "",
        mobile_no: ""
      }
    };
  },
  methods: {
    async verifyCaptchaAndSendOTP() {
      if (this.captchaValue == "" || this.uid == "" || this.uid.length < 12) {
        this.$toast.open({
          message:
            'Fillup captcha and aadhaar number . Then click on "Generate OTP"',
          type: "warning",
          duration: 2000,
          dismissible: true
        })
        return;
      }
      var payload = {
        'captchaTxnId': this.captchaTxnId,
        'captchaValue': this.captchaValue,
        'uid': this.uid 
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request/otp/", "", false);
      if (response["success"]) {
        this.otp_transaction_id = response["payload"]["otp_transaction_id"];
        this.request_transaction_id = response["payload"]["request_transaction_id"];
        this.iscaptchaverified = true;
      } else {
        var data = await getCaptcha();
        this.captchaTxnId = data["captchaTxnId"];
        this.captchaBase64 = "data:image/jpeg;base64," + data["captchaBase64String"];
      }
      console.log(response);
    },
    async verifyOTP(){
      if (this.otp == "" || this.otp.length < 6) {
        this.$toast.open({
          message: 'Enter 6 digit OTP. Then click on "Verify OTP"',
          type: "warning",
          duration: 2000,
          dismissible: true
        })
        return;
      }
      let payload = {
        'request_id': this.$route.params.request_id,
        'otp_transaction_id': this.otp_transaction_id,
        'otp': this.otp,
        'uid': this.uid 
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request_approval/ekyc/", "", false);
      if(response["success"]){
        this.jwt_token = response["payload"]["jwt_token"];
        this.user.name = response["payload"]["user"]["name"];
        this.user.photo = "data:image/jpeg;base64," + response["payload"]["user"]["photo"];
        this.user.mobile_no = response["payload"]["user"]["mobile_no"];
        this.step = 2;
      }
      console.log(response);
    },
    async submitDecision(decision){
      let payload = {
        'approve_action': decision,
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request_approval/decision/", this.jwt_token, true);

      console.log(response);
    }
  },
};
</script>
