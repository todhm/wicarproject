import React,{Fragment} from 'react';
import {
  Table,
  TableBody,
  TableHead,
  TableCell,
  TableRow,
  Checkbox,
  Collapse
} from '@material-ui/core';
import {connect} from 'react-redux'
import {AdminReducerToProps} from '../utils/reducerutils';
import * as adminAction from './action'

import ChildTable from './ChildTable';

const ParentTable = (props) => {
  const{unpaidList,allCheck,changeCheck,changeAllCheck} = props;
return(
    <Table>
      <TableHead>
        <TableRow>
          <TableCell><Checkbox checked={allCheck} onChange={(e)=>changeAllCheck()}  /></TableCell>
          <TableCell>차주명</TableCell>
          <TableCell>차주계좌주명</TableCell>
          <TableCell>차주전화번호</TableCell>
          <TableCell>차주계좌번호</TableCell>
          <TableCell>총지급금액</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
      {unpaidList?Object.keys(unpaidList).map((key)=>(
        <Fragment key={key}>
        <TableRow>
          <TableCell> <Checkbox checked={unpaidList[key].checked} value="true" onChange={(e)=>changeCheck(key,!unpaidList[key].checked)} /></TableCell>
          <TableCell>{unpaidList[key].owner_name}</TableCell>
          <TableCell>{unpaidList[key].account_holder_name}</TableCell>
          <TableCell>{unpaidList[key].owner_phone}</TableCell>
          <TableCell>{unpaidList[key].account_num}</TableCell>
          <TableCell>{unpaidList[key].total_earning}</TableCell>
        </TableRow>
        <TableRow>
          <TableCell
            colSpan={5}
            children={<ChildTable bookingList={unpaidList[key].booking_list} />}
          />
        </TableRow>
        </Fragment>
      )):null}
      </TableBody>
    </Table>
  );


}
export default connect(AdminReducerToProps, adminAction)(ParentTable);
