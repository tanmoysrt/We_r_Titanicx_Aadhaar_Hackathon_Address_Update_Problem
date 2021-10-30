<template>
  <div v-if="step == 1">
    <form>
      <div class="input-field aadhar-field">
        <label for="">Enter your 12 digit Aadhar number</label>
        <input type="number" maxlength="12" v-model="uid" :disabled="iscaptchaverified" />
      </div>
      <div class="row">
        <div class="captcha"><img :src="captchaBase64" alt="loading.." /></div>
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
    <div class="grid">
      <div class="input-field">
          <label for="">House No</label>
          <input  type="text" v-model="landlord_address.house" />
      </div>
      <div class="input-field">
          <label for="">Landmark</label>
          <input type="text" v-model="landlord_address.landmark" />
      </div>
      <div class="input-field">
          <label for="">Street Name</label>
          <input  type="text" v-model="landlord_address.street" />
      </div>
      <div class="input-field">
          <label for="">Location</label>
          <input type="text" v-model="landlord_address.loc" />
      </div>
      <div class="input-field">
          <label for="">Village/Town/City</label>
          <input type="text" v-model="landlord_address.vtc"  disabled />
      </div>
      <div class="input-field">
          <label for="">Post Office</label>
          <input type="text" v-model="landlord_address.po" disabled />
      </div>
      <div class="input-field">
          <label for="">Sub-District</label>
          <input type="text" v-model="landlord_address.subdist" disabled />
      </div>
      <div class="input-field">
          <label for="">District</label>
          <input type="text" v-model="landlord_address.dist" disabled />
      </div>
      <div class="input-field">
          <label for="">State</label>
          <input type="text" v-model="landlord_address.state" disabled />
      </div>
      <div class="input-field">
          <label for="">Pincode</label>
          <input  type="text" v-model="landlord_address.pc" />
      </div>
  </div>

    <div class="btn-row">
      <button class=" btn-primary" v-on:click.stop.prevent="reset_address()">RESET ADDRESS</button>
      <button class=" btn-primary" v-on:click.stop.prevent="check_address()">CHECK ADDRESS</button>
      <button class=" btn-primary btn-green" v-on:click.stop.prevent="submit_address()">SUBMIT ADDRESS</button>
    </div>

  </div>
</template>

<script>
import helper from "../helper_functions";

async function getCaptcha(){
  var responseCaptcha = await helper.REST_API(()=>{}, {}, "/request/captcha/", "", false, "get", true);
  if (responseCaptcha["success"]) {
    console.log(responseCaptcha);
    return responseCaptcha["payload"];
  }
  return "-1";
}

export default {
  name: "Approve Consent",
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
      landlord_name: "",
      landlord_contact_no: "",
      landlord_previous_address: {
        house: "",
        landmark: "",
        loc: "",
        po: "",
        pc: "",
        dist: "",
        subdist: "",
        vtc: "",
        street: "",
        state: "",
        country: ""
      },
      landlord_address: {
        house: "",
        landmark: "",
        loc: "",
        po: "",
        pc: "",
        dist: "",
        subdist: "",
        vtc: "",
        street: "",
        state: "",
        country: ""
      },
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
        request_id: this.$route.params.request_id,
        otp_transaction_id: this.otp_transaction_id,
        'otp': this.otp,
        'uid': this.uid 
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request/ekyc_id/", "", false);
      this.jwt_token = response["payload"]["jwt_token"];
      if(response["payload"]["request_status"] == "approved_by_landlord"){
        await this.load_address();
      }else if (response["payload"]["request_status"] == "requested"){
        this.notification_redirection_decision({
          "success" : true,
          "message" : "Consent request has been sent to landlord ! He/She has not taken any action till now",
          "error" : "",
          "page_show" : true
        })
      }else if (response["payload"]["request_status"] == "rejected_by_landlord"){
        this.notification_redirection_decision({
          "success" : false,
          "message" : "Consent has been rejected by landlord",
          "error" : "",
          "page_show" : true
        })
      }else if (response["payload"]["request_status"] == "rejected_by_system"){
        this.notification_redirection_decision({
          "success" : false,
          "message" : "Consent has been rejected automatically by system",
          "error" : "",
          "page_show" : true
        })
      }else if (response["payload"]["request_status"] == "failed_due_to_limit_reach_of_landlord"){
        this.notification_redirection_decision({
          "success" : false,
          "message" : "Landlord has reached his limit of issuing consent ! So can't accpet consent more ",
          "error" : "",
          "page_show" : true
        })
      }else if (response["payload"]["request_status"] == "updated"){
        this.notification_redirection_decision({
          "success" : true,
          "message" : "Aadhaar updated already ! No action needed",
          "error" : "",
          "page_show" : true
        })
      }

      console.log(response);
    },
    async load_address(){
      let payload = {};
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request/lanlord_approved_adddress/", this.jwt_token, true);
      this.landlord_name = response["payload"]["landlord_name"];
      this.landlord_contact_no = response["payload"]["landlord_mobile_no"];
      this.landlord_address = response["payload"]["landlord_address"];
      this.landlord_previous_address = Object.assign({}, response["payload"]["landlord_address"]);
      this.step = 2;
      console.log(response);
    },
    reset_address(){
      this.landlord_address = Object.assign({}, this.landlord_previous_address);
    },
    async check_address(){
      let payload = {
        'updated_address' : this.landlord_address
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request/verify_address_distance/", this.jwt_token, true, "post", true);
      console.log(response);
    },
    async submit_address(){
      let payload = {
        'uid' : this.uid,
        'updated_address' : this.landlord_address
      };
      var response = await helper.REST_API(this.notification_redirection_decision, payload, "/request/submit_update/", this.jwt_token, true, "post", true);
      console.log(response);
    },
  },
};
</script>
