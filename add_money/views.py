from add_money import add_money_bp
from flask import render_template, request, redirect, url_for, flash, make_response
from flaskext.login import login_required, current_user
from models import validate_float, add_to_user_balance

from urllib import unquote_plus
from paypal import SetExpressCheckoutDG, GetExpressCheckoutDetails
from paypal import ConfirmPayment, RedirectToPayPal, RedirectToPayPalDG


@add_money_bp.route('/addMoney')
@login_required
def add_money_view():
    return render_template('add_money.html')


@add_money_bp.route('/addMoney/valueError')
@login_required
def value_error_money():
    return render_template('value_error.html')


@add_money_bp.route('/addMoney/checkout', methods=['GET', 'POST'])
@login_required
def paypal_checkout():

    paymentAmount = 0
    payment = request.form.get('amount')
    if(validate_float(payment)):
        paymentAmount = payment
    else:
        flash('<strong>Payment Error</strong> Enter a valid number!', 'error')
        return redirect(url_for('.value_error_money'))

    currencyCodeType = "USD"
    paymentType = "Sale"

    returnURL = "http://127.0.0.1:5000/addMoney/confirm"

    cancelURL = "http://127.0.0.1:5000/addMoney/cancel"

    items = [{'name': 'LVL1 Store Credit', 'amt': paymentAmount, 'qty': 1}]

    resArray = SetExpressCheckoutDG(paymentAmount, currencyCodeType,
        paymentType, returnURL, cancelURL, items)

    ack = resArray["ACK"].upper()
    if(ack == "SUCCESS" or ack == "SUCCESSWITHWARNING"):
        token = unquote_plus(resArray["TOKEN"])
        return RedirectToPayPalDG(token)
    else:
        ErrorCode = unquote_plus(resArray["L_ERRORCODE0"])
        ErrorShortMsg = unquote_plus(resArray["L_SHORTMESSAGE0"])
        ErrorLongMsg = unquote_plus(resArray["L_LONGMESSAGE0"])
        ErrorSeverityCode = unquote_plus(resArray["L_SEVERITYCODE0"])

        return make_response("""SetExpressCheckout API call failed.
        Detailed Error Message: """ + ErrorLongMsg + """
        Short Error Message: """ + ErrorShortMsg + """
        Error Code: """ + ErrorCode + """
        Error Severity Code: """ + ErrorSeverityCode)


@login_required
@add_money_bp.route('/addMoney/confirm', methods=['GET', 'POST'])
def confirm():
    res = GetExpressCheckoutDetails(request.args['token'])

    finalPaymentAmount = res["AMT"]

    token = request.args['token']
    payerID = request.args['PayerID']
    paymentType = 'Sale'
    currencyCodeType = res['CURRENCYCODE']

    resArray = ConfirmPayment(token, paymentType, currencyCodeType, payerID,
        finalPaymentAmount)
    ack = resArray["ACK"].upper()
    if(ack == "SUCCESS" or ack == "SUCCESSWITHWARNING"):
        transactionId = resArray["PAYMENTINFO_0_TRANSACTIONID"]
        transactionType = resArray["PAYMENTINFO_0_TRANSACTIONTYPE"]
        paymentType = resArray["PAYMENTINFO_0_PAYMENTTYPE"]
        orderTime = resArray["PAYMENTINFO_0_ORDERTIME"]
        amt = resArray["PAYMENTINFO_0_AMT"]
        currencyCode = resArray["PAYMENTINFO_0_CURRENCYCODE"]
        feeAmt = resArray["PAYMENTINFO_0_FEEAMT"]
    #  settleAmt = resArray["PAYMENTINFO_0_SETTLEAMT"]
        taxAmt = resArray["PAYMENTINFO_0_TAXAMT"]
    #  exchangeRate = resArray["PAYMENTINFO_0_EXCHANGERATE"]

        paymentStatus = resArray["PAYMENTINFO_0_PAYMENTSTATUS"]

        pendingReason = resArray["PAYMENTINFO_0_PENDINGREASON"]

        reasonCode = resArray["PAYMENTINFO_0_REASONCODE"]
        
        add_to_user_balance(current_user.id, float(amt))

        flash('Payment Successful!', 'success')
        return render_template('confirm.html', paymentfailure=False)
    else:
        print "Payment Failed"
        ErrorCode = unquote_plus(resArray["L_ERRORCODE0"])
        ErrorShortMsg = unquote_plus(resArray["L_SHORTMESSAGE0"])
        ErrorLongMsg = unquote_plus(resArray["L_LONGMESSAGE0"])
        ErrorSeverityCode = unquote_plus(resArray["L_SEVERITYCODE0"])

        errStr = """DoExpressCheckoutDetails API call failed.
        Detailed Error Message: """ + ErrorLongMsg + """
        Short Error Message: """ + ErrorShortMsg + """
        Error Code: """ + ErrorCode + """
        Error Severity Code: """ + ErrorSeverityCode
        return render_template('confirm.html', paymentfailure=True,
            errorstring=errStr)
