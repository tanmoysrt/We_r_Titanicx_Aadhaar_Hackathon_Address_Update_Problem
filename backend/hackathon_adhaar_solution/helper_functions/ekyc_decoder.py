from hashlib import sha256
import base64

def isEmptyString(string):
    if str(string).strip() == "":
        return True
    return False

class POA:
    careof = ""
    country = ""
    dist = ""
    house = ""
    landmark = ""
    loc = ""
    pc = ""
    po = ""
    state = ""
    street = ""
    subdist = ""
    vtc = ""

    def __init__(self, input, from_json=False):
        if not from_json:
            self.careof = input.get("careof")
            self.country = input.get("country")
            self.dist = input.get("dist")
            self.house = input.get("house")
            self.landmark = input.get("landmark")
            self.loc = input.get("loc")
            self.pc = input.get("pc")
            self.po = input.get("po")
            self.state = input.get("state")
            self.street = input.get("street")
            self.subdist = input.get("subdist")
            self.vtc = input.get("vtc")
        else:
            if "careof" in input:
                self.careof = input["careof"]
            if "house" in input:
                self.house = input["house"]
            if "landmark" in input:
                self.landmark = input["landmark"]
            if "loc" in input:
                self.loc = input["loc"]
            if "po" in input:
                self.po = input["po"]
            if "pc" in input:
                self.pc = input["pc"]
            if "dist" in input:
                self.dist = input["dist"]
            if "dist" in input:
                self.dist = input["dist"]
            if "subdist" in input:
                self.subdist = input["subdist"]
            if "vtc" in input:
                self.vtc = input["vtc"]
            if "street" in input:
                self.street = input["street"]
            if "country" in input:
                self.country = input["country"]


    def to_json(self):
        data = {
            "careof": self.careof,
            "house": self.house,
            "landmark": self.landmark,
            "loc": self.loc,
            "po": self.po,
            "pc": self.pc,
            "dist": self.dist,
            "subdist": self.subdist,
            "vtc": self.vtc,
            "street": self.street,
            "state": self.state,
            "country": self.country
        }
        return data

    def to_serialized_format(self):
        address = ""
        list_params = [self.house, self.loc, self.landmark, self.street, self.vtc, self.po, self.subdist, self.dist, self.state, self.country, self.pc]

        for i in range(0, len(list_params)):
            if not isEmptyString(list_params[i]):
                address += list_params[i]

                if i < len(list_params)-1:
                    address += ", "

        return address


class POI:
    dob = ""
    e = ""
    gender = ""
    m = ""
    name = ""

    def __init__(self, xml):
        self.dob = xml.get("dob")
        self.e = xml.get("e")
        self.gender = xml.get("gender")
        self.m = xml.get("m")
        self.name = xml.get("name")

    def verify_mobile_no(self, mobile_no, share_code, last_digit_uid):
        str_data = str(mobile_no) + str(share_code)
        tmp_sha = sha256(str_data.encode()).hexdigest()

        if not (last_digit_uid == 0 or last_digit_uid == 1):
            for i in range(last_digit_uid - 1):
                tmp_sha = sha256(tmp_sha.encode()).hexdigest()
        return tmp_sha == self.m

    def to_json(self):
        data = {
            "name": self.name,
            "gender": self.gender,
            "dob": self.dob,
            "e": self.e,
            "m": self.m
        }
        return data


class OfflinePaperlessKycData:
    referenceId = ""
    poa = None
    poi = None
    pht = None

    def __init__(self, xml):
        self.referenceId = xml.get("referenceId")
        uidData = list(xml)[0]
        self.poi = POI(list(uidData)[0])
        self.poa = POA(list(uidData)[1])
        self.pht = list(uidData)[2].text

    def pht_base64(self):
        return base64.b64decode(self.pht)

    def to_json(self, with_photo=True):
        data = {}
        data["referenceId"] = self.referenceId
        data["poa"] = self.poa.to_json()
        data["poi"] = self.poi.to_json()
        if with_photo:
            data["pht"] = self.pht
        return data
