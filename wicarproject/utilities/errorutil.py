from flask import jsonify

def return_booking_error(result):
    result['message'] = "fail"
    result['errorMessage']="해당날짜에는 예약이 불가능합니다. 다른날짜를 선택해주세요."
    return result

def convert_error_by_field(result,form):
    result['message']="fail"
    error_list = []
    for field, errors in form.errors.items():
        errorKey= field + "Error"
        result['errorMessage'] = {errorKey:errors[0]}
    return result
