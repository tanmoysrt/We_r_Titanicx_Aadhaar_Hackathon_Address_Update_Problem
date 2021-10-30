import axios from "axios";
const qs = require("qs");

const EDNPOINT = "https://devhunt.in";

// eslint-disable-next-line prettier/prettier
const REST_API = async (callback, payload,route,auth_token = "",use_auth = false,_method = "post",format_is_json=false) => {
  let data;
  if (format_is_json) {
    data = JSON.stringify(payload);
  } else {
    data = qs.stringify(payload);
  }
  let headers = {
    "Content-Type": "application/x-www-form-urlencoded",
  };

  if (format_is_json) {
    headers["Content-Type"] = "application/json";
  }

  if (use_auth) {
    headers["Authorization"] = "Bearer " + auth_token;
  }

  let config = {
    method: _method,
    url: EDNPOINT + route,
    headers: headers,
    data: data,
  };

  var res = await axios.request(config);
  callback(res.data);
  return res.data;
};

export default {
  REST_API,
};
