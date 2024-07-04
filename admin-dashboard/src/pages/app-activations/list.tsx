import React, { useEffect, useState } from 'react';
import { Table, Button, Space, notification } from 'antd';
import axios from 'axios';
import { useTable } from '@refinedev/antd';
import { useApiUrl, useList } from '@refinedev/core';

interface AppActivation {
  id: number;
  activation_code: string;
  activations_limit: number;
  created_at: string;
  desctiption: string;
  confirmed_at: string;
  amount_of_uses: number;
}

export const AppActivationsList: React.FC = () => {
  const { data: activations, error, isLoading } = useList<AppActivation>();
  const { tableProps } = useTable<AppActivation>();

  const apiUrl = useApiUrl();

  const columns = [
    {
      title: 'Activation Code',
      dataIndex: 'activation_code',
      key: 'activation_code',
    },
    {
      title: 'Created At (UTC)',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (text: any, record: AppActivation) => {
        const dateandtime = (text as string).split('T');
        return <div>{dateandtime[0]} {dateandtime[1].substring(0, 5)}</div>
      }
    },
    {
      title: 'Expires At (UTC)',
      dataIndex: 'expires_at',
      key: 'expires_at',
      render: (text: any, record: AppActivation) => {
        const dateandtime = (text as string).split('T');
        return <div>{dateandtime[0]} {dateandtime[1].substring(0, 5)}</div>
      }
    },
    {
      title: 'Limit',
      dataIndex: 'activations_limit',
      key: 'activations_limit',
    },
    {
      title: 'Amount of Uses',
      dataIndex: 'amount_of_uses',
      key: 'amount_of_uses',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    },
  ];

  return (
    <div>
      <h2>App Activations</h2>
      <Table
        {...tableProps}
        columns={columns}
        dataSource={activations?.data}
        rowKey="id"
      />
    </div>
  );
};