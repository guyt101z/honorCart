import pycurl
from urllib import quote_plus, unquote_plus
from urlparse import parse_qsl
from flask import redirect, session
import StringIO

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 808

from config import API_UserName, API_Password, API_Signature, SandboxFlag

sBNCode = "PP-ECWizard"

if(SandboxFlag):
    API_Endpoint = "https://api-3t.sandbox.paypal.com/nvp"
    PAYPAL_URL = "https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&token="
    PAYPAL_DG_URL = "https://www.sandbox.paypal.com/incontext?token="
else:
    API_Endpoint = "https://api-3t.paypal.com/nvp"
    PAYPAL_URL = "https://www.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="
    PAYPAL_DG_URL = "https://www.paypal.com/incontext?token="

USE_PROXY = False
version = "84"


def SetExpressCheckoutDG(paymentAmount, currencyCodeType, paymentType, returnURL,
                                        cancelURL, items):
#    //------------------------------------------------------------------------------------------------------------------------------------
#    // Construct the parameter string that describes the SetExpressCheckout API call in the shortcut implementation    $nvpstr = "&PAYMENTREQUEST_0_AMT=". $paymentAmount;

    nvpstr = "&PAYMENTREQUEST_0_AMT=" + paymentAmount
    nvpstr += "&PAYMENTREQUEST_0_PAYMENTACTION=" + paymentType
    nvpstr += "&RETURNURL=" + returnURL
    nvpstr += "&CANCELURL=" + cancelURL
    nvpstr += "&PAYMENTREQUEST_0_CURRENCYCODE=" + currencyCodeType
    nvpstr += "&REQCONFIRMSHIPPING=0"
    nvpstr += "&NOSHIPPING=1"

    for index, item in enumerate(items):
        nvpstr += "&L_PAYMENTREQUEST_" + str(index) + "_NAME0=" + item["name"]
        nvpstr += "&L_PAYMENTREQUEST_" + str(index) + "_AMT0=" + item["amt"]
        nvpstr += "&L_PAYMENTREQUEST_" + str(index) + "_QTY0=" + str(item["qty"])
        nvpstr += "&L_PAYMENTREQUEST_" + str(index) + "_ITEMCATEGORY0=Digital"

    resArray = hash_call("SetExpressCheckout", nvpstr)
    ack = resArray["ACK"].upper()
    if(ack == "SUCCESS" or ack == "SUCCESSWITHWARNING"):
        token = unquote_plus(resArray["TOKEN"])
        session['TOKEN'] = token

    return resArray


def GetExpressCheckoutDetails(token):

    nvpstr = "&TOKEN=" + token

    resArray = hash_call("GetExpressCheckoutDetails", nvpstr)
    ack = resArray["ACK"].upper()
    if(ack == "SUCCESS" or ack == "SUCCESSWITHWARNING"):
        return resArray
    else:
        return False


def ConfirmPayment(token, paymentType, currencyCodeType, payerID, FinalPaymentAmt):
    token = quote_plus(token)
    paymentType = quote_plus(paymentType)
    currencyCodeType = quote_plus(currencyCodeType)
    payerID = quote_plus(payerID)
    serverName = quote_plus("localhost")

    nvpstr = '&TOKEN=' + token + '&PAYERID=' + payerID + '&PAYMENTREQUEST_0_PAYMENTACTION=' + paymentType + '&PAYMENTREQUEST_0_AMT=' + FinalPaymentAmt
    nvpstr += '&PAYMENTREQUEST_0_CURRENCYCODE=' + currencyCodeType + '&IPADDRESS=' + serverName

    resArray = hash_call("DoExpressCheckoutPayment", nvpstr)

    ack = resArray["ACK"].upper()

    return resArray


def RedirectToPayPal(token):
    payPalURL = PAYPAL_URL + token
    redirect(payPalURL)


def RedirectToPayPalDG(token):
    payPalURL = PAYPAL_URL + token
    return redirect(payPalURL)


def hash_call(methodName, nvpStr):
    #declaring of global variables

    #setting the curl parameters.
    pycurl.global_init(pycurl.GLOBAL_DEFAULT)
    ch = pycurl.Curl()
    ch.setopt(pycurl.URL, API_Endpoint)
    ch.setopt(pycurl.VERBOSE, 1)

    #turning off the server and peer verification(TrustManager Concept).
    ch.setopt(pycurl.SSL_VERIFYPEER, False)
    ch.setopt(pycurl.SSL_VERIFYHOST, False)

    #ch.setopt(pycurl.RETURNTRANSFER, 1)
    ch.setopt(pycurl.POST, 1)

    #if USE_PROXY constant set to TRUE in Constants.php, then only proxy will be enabled.
    #Set proxy name to PROXY_HOST and port number to PROXY_PORT in constants.php
    if(USE_PROXY):
        ch.setopt(pycurl.PROXY, PROXY_HOST + ":" + PROXY_PORT)

    #NVPRequest for submitting to server
    nvpreq = "METHOD=" + quote_plus(methodName) + "&VERSION=" + quote_plus(version) + "&PWD=" + quote_plus(API_Password) + "&USER=" + quote_plus(API_UserName) + "&SIGNATURE=" + quote_plus(API_Signature) + nvpStr + "&BUTTONSOURCE=" + quote_plus(sBNCode)

    #setting the nvpreq as POST FIELD to curl
    ch.setopt(pycurl.POSTFIELDS, str(nvpreq))
    b = StringIO.StringIO()
    ch.setopt(pycurl.WRITEFUNCTION, b.write)

    #getting response from server
    ch.perform()

    response = b.getvalue()

    #onvrting NVPResponse to an Associative Array
    nvpResArray = deformatNVP(response)
    nvpReqArray = deformatNVP(nvpreq)
    session['nvpReqArray'] = nvpReqArray

    if (ch.errstr()):
        #moving to display page to display curl errors
        session['curl_error_msg'] = ch.errstr()

       # $Execute the Error handling module to display errors.
    else:
        ch.close()

    return nvpResArray


def deformatNVP(nvpstr):

    return dict(parse_qsl(nvpstr))
