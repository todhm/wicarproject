import React from 'react';
import {
  Table,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '@material-ui/core';

const ChildTable = (props) =>{
  const {bookingList} = props;
  return (
    <Table>
      <TableHead>
        <TableRow>
        <TableCell></TableCell>
        <TableCell>예약시작일</TableCell>
        <TableCell>예약종료일</TableCell>
        <TableCell>대여자명</TableCell>
        <TableCell>지급금액</TableCell>
        <TableCell></TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
      {bookingList?bookingList.map((booking_info)=>(
        <TableRow key={booking_info.id}>
          <TableCell></TableCell>
          <TableCell>{booking_info.start_time}</TableCell>
          <TableCell>{booking_info.end_time}</TableCell>
          <TableCell>{booking_info.renter_name}</TableCell>
          <TableCell>{booking_info.owner_earning}</TableCell>
          <TableCell></TableCell>
        </TableRow>
      )):null}
      </TableBody>
    </Table>
  );
}


export default ChildTable;
