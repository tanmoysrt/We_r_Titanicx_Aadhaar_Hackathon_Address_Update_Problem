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
    <form>
      <p>Enter a valid contact number of you where you will get all updates</p>
      <div class="row">
        <div class="input-field ph-num-field">
          <input type="number" maxlength="8" v-model="mobile_number" />
          <p> <img src="img/indianflag.png" alt="">+91</p>
        </div>
        <button class="btn-primary send-link-btn" v-on:click.stop.prevent="submitMobileNumber">SUBMIT</button>
      </div>
    </form>
  </div>

  <div v-if="step == 3">
    <form>
      <p>Enter the phone number of the landlord/neighbour for approval of Aadhaar Updation consent</p>
      <div class="row">
        <div class="input-field ph-num-field">
          <input type="number" maxlength="8" v-model="landlord_mobile_number" />
          <p> <img src="img/indianflag.png" alt="">+91</p>
        </div>
        <button class="btn-primary send-link-btn" v-on:click.stop.prevent="submitLandlordMobileNumber">SUBMIT</button>
      </div>
    </form>
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
  name: "Register Request",
  components: {},
  props: ['notification_redirection_decision'],
  async mounted() {
    var data = await getCaptcha();
    this.captchaTxnId = data["captchaTxnId"];
    this.captchaBase64 = "data:image/jpeg;base64," + data["captchaBase64String"];
  },
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
      mobile_number: "",
      landlord_mobile_number: ""
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
      if(response["success"]){
        this.otp_transaction_id = response["payload"]["otp_transaction_id"];
        this.request_transaction_id = response["payload"]["request_transaction_id"];
        this.iscaptchaverified = true;
      }else{
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
        'request_transaction_id': this.request_transaction_id,
        'otp_transaction_id': this.otp_transaction_id,
        'otp': this.otp,
        'uid': this.uid 
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request/ekyc/", "", false);
      if(response["success"]){
        this.jwt_token = response["payload"]["jwt_token"];
        this.request_status = response["payload"]["request_status"];
        this.step = 2;
      }
      console.log(response);
    },
    async submitMobileNumber(){
      if (this.mobile_number.length < 10) {
        this.$toast.open({
          message: 'Enter 10 digit valid mobile number and press submit',
          type: "error",
          duration: 2000,
          dismissible: true
        })
        return;
      }
      let payload = {
        'mobile_number': this.mobile_number 
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/update/user_mobile/", this.jwt_token, true);
      if (response["success"]) {
          this.step = 3;
      }
      console.log(response);
    },
    async submitLandlordMobileNumber(){
      if (this.landlord_mobile_number.length < 10) {
        this.$toast.open({
          message: 'Enter 10 digit valid mobile number and press submit',
          type: "error",
          duration: 2000,
          dismissible: true
        })
        return;
      }
      let payload = {
        'landlord_mobile_number': this.landlord_mobile_number 
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/update/landlord_mobile/", this.jwt_token, true);
      if(response["success"]){
        this.step = 4;
      }
      console.log(response);
    }
  },
};
</script>
