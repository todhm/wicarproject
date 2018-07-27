export const guid=()=> {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

export const getAdvanceNoticeOptions = (timeList) =>{
    return timeList.map((time)=>{
        if(time==0){
            return {value:time,label:"상시가능"};
        }
        else if(time >0 && time < 24){
            let labelString = time.toString() + " 시간";
            return { value:time, label:labelString};

        }
        else if(time >=24 && time < 168){
            let labelString = parseInt(time/24,10).toString() + " 일";
            return { value:time, label:labelString};
        }
        else{
            let labelString = parseInt(time/168,10).toString() + " 주";
            return { value:time, label:labelString};

        }
    })
}
