export const range=(lowEnd,highEnd)=>{
    var arr = [],
   c = highEnd - lowEnd + 1;
   while ( c-- ) {
       arr[c] = highEnd--
   }
   arr = arr.map((x)=>({label:x,value:x}))
   return arr;
}
