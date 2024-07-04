import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useApiUrl } from "@refinedev/core";
import { useForm } from "@refinedev/antd";
import { Form, Input, Button } from "antd";

export const CreateAppActivation = () => {
  const { form, formProps, formLoading } = useForm();
  const navigate = useNavigate();
  const apiUrl = useApiUrl();

  const onSubmit = async (values: any) => {
    try {
      const response = await axios.post(`${apiUrl}/auth/app-activations/create-code`, values, {
        headers: {
          "Authorization": "Bearer " + (localStorage.getItem("token") as string),
          "Content-Type": "application/json"
        }
      });
      if (response.status === 201) {
        alert("Activation code created successfully!");
        navigate("/activation");
      }
    } catch (error) {
      console.error("Error creating activation code:", error);
      alert("Failed to create activation code.");
    }
  };

  return (
    <div>
      <h2>Create App Activation</h2>
      <Form {...formProps} form={form} onFinish={onSubmit}>
        <Form.Item
          label="Activations Limit"
          name="activations_limit"
          rules={[{ required: true, message: "This field is required" }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item
          label="Expires In Days"
          name="expires_in_days"
          rules={[{ required: true, message: "This field is required" }]}
        >
          <Input type="number" />
        </Form.Item>
        <Form.Item
          label="Description"
          name="description"
          rules={[{ required: true, message: "This field is required" }]}
        >
          <Input type="text" />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={formLoading}>
          Create Activation Code
        </Button>
      </Form>
    </div>
  );
};