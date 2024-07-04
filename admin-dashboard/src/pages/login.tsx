import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { updateToken } from '../App';

import { Form, Input, Button, notification, Card, Row, Col, Typography, Modal } from 'antd';
import { API_URL } from '../providers/data-provider';

const { Title } = Typography;

const Login = ({ onClose }: { onClose?: () => void }) => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  
  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const response = await axios.post(API_URL + '/auth/login', values);
      localStorage.setItem('token', response.data.token);
      updateToken(response.data.token);
      notification.success({ message: 'Login successful!' });
      if (onClose && typeof onClose === 'function') {
        onClose();
      } else {
        navigate('/recipes');
      }
      
    } catch (error) {
      notification.error({ message: `Login failed. ${(error as Error).message}` });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Row justify="center" align="middle" style={{ height: '100vh' }}>
      <Col>
        <Card style={{ width: 400, textAlign: 'center', padding: '20px' }}>
          <Title level={2}> Login </Title>
          <Form
            name="login"
            onFinish={onFinish}
            layout="vertical"
            initialValues={{ remember: true }}
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: 'Please input your username!' }]}
            >
              <Input placeholder="Username" />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Please input your password!' }]}
            >
              <Input.Password placeholder="Password" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} block> Login </Button>
            </Form.Item>
          </Form>
        </Card>
      </Col>
    </Row>
  );
};

const LoginModal = ({ visible, onClose }: { visible: boolean; onClose: () => void }) => {
  return (
    <Modal
      title="Login"
      open={visible}
      onCancel={onClose}
      footer={null}
    >
      <Login onClose={onClose} />
    </Modal>
  );
};

export {Login, LoginModal};
