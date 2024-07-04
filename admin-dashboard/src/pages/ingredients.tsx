import React, { useState } from "react";

import { useList, useSelect, BaseKey, useApiUrl } from "@refinedev/core";
import { axiosInstance } from "../App";

import { Button, Form, FormProps, Input, Select, Space, Table } from "antd";
import { EditButton } from "@refinedev/antd";
import { CheckOutlined, CloseOutlined, MinusCircleOutlined } from "@ant-design/icons";
import { FormListFieldData } from "antd/lib";


export const ListIngredient = () => {
  const { data, error, isLoading, refetch } = useList({ resource: "ingredients" });
  const [editingRow, setEditingRow] = useState<BaseKey | undefined>(undefined);
  const [editingName, setEditingName] = useState<string | undefined>(undefined);
  const apiUrl = useApiUrl();
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const sortedData = [...(data?.data || [])].sort((a, b) => a.name.localeCompare(b.name));
  
  return (
    <Table
    dataSource={sortedData}
    columns={[{
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => {
        if (editingRow === record.id) {
          return (
            <Space>
              <Input
                defaultValue={editingName}
                onInput={(e) => { setEditingName(e.currentTarget.value); }}
              />
              <Button
                type="dashed"
                icon={<CloseOutlined />}
                onClick={() => {
                  setEditingRow(undefined);
                  setEditingName(undefined);
                }}
              />
              <Button
                type="primary"
                icon={<CheckOutlined />}
                onClick={ async () => {
                  try {
                    await axiosInstance.put(`${apiUrl}/ingredients/${record.id}`, {
                      name: editingName,
                    }, {
                      headers: { "Content-Type": "application/json" }
                    });
                  } catch (error) {
                    console.error(error);
                  } finally {
                    setEditingRow(undefined);
                    setEditingName(undefined);
                    await refetch();
                  }
                }}
              />
            </Space>
          );
        } else {
          return (
            <div>
              {text}
              <EditButton style={{ float: "right" }} onClick={() => { setEditingRow(record.id); setEditingName(text) }} hideText />
            </div>
          );
        }
      }
    }]}
    />
  );
};

interface IngInputProps {
  value: string;
  onChange: (value: string) => void;
}

export const IngredientSelect: React.FC<IngInputProps> = ({ value, onChange }) => {
  const selected = value && value[0] !== "#" && value[0] !== "*" ? "#" + value : value;
  const [searchText, setSearchText] = useState('');
  
  const filterOption = (input: string, option?: { label: string; value: string }) =>
    (option?.label ?? '').toLowerCase().includes(input.toLowerCase());
  
  const { options: ing_options } = useSelect({
    resource: "ingredients",
    optionLabel: "name",
    optionValue: "id"
  });
  
  const table_opts = (ing_options)?.map((ingredient) => (
    {
      value: "#" + ingredient.value,
      label: ingredient.label,
    }
  ));

  const selectSwitch = <Select
  showSearch
  placeholder="Select an ingredient or type a new one"
  optionFilterProp="children"
  onChange={onChange}
  onSearch={setSearchText}
  filterOption={filterOption}
  options={table_opts}
  style={{ width: 200 }}
  value={selected}
  />
  
  if (searchText != "") {
    table_opts.unshift({value: "*" + searchText, label: searchText + " (new)"});
  }
  
  return selectSwitch;
}

interface IngredientFormProps {
  formProps: FormProps<{}>;
  field: FormListFieldData;
  ingToUnitDict: { [key: string]: string };
  remove: () => void;
  }

export const IngredientForm: React.FC<IngredientFormProps> = ({ formProps, field, ingToUnitDict, remove }) => {
  function handleIngredientChange(value: string) {
    if (value !== "") {
      const unitByIng = ingToUnitDict[value.slice(1)];
      if (unitByIng) {
        const ingredients = formProps.form?.getFieldValue('ingredients');
        const updatedIngredient = { ...ingredients[field.key], unit: unitByIng };
        ingredients[field.key] = updatedIngredient;
        formProps.form?.setFieldValue('ingredients', ingredients);
      }
    }
  }

  return (
    <Space key={field.key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
      <Form.Item
        name={[field.name, 'id']}
        rules={[{ required: true, message: 'Missing ingredient' }]}
      >
        <IngredientSelect value="" onChange={handleIngredientChange}/>
      </Form.Item>
      <Form.Item
        name={[field.name, 'qty']}
        rules={[{ required: true, message: 'Missing quantity' }]}
      >
        <Input type="number" />
      </Form.Item>
      <Form.Item
        name={[field.name, 'unit']}
        rules={[{ required: true, message: 'Missing unit' }]}
      >
        <Select
          style={{ minWidth: 100 }}
          options={[
            { label: "pinch", value: "pinch" },
            { label: "piece", value: "piece" },
            { label: "kg", value: "kg" },
            { label: "gram", value: "gram" },
            { label: "ml", value: "ml" },
            { label: "liter", value: "liter" },
            { label: "cup", value: "cup" }
          ]}
        />
      </Form.Item>
      <MinusCircleOutlined onClick={remove} />
    </Space>
  )
}

export const useIngToUnitDict = () => {
  const { data: ingUnitList, isSuccess } = useList<{ ingredient_id: string, unit: string }>({ resource: "ingredients/units" });
  if (!isSuccess) return null;
  return ingUnitList.data.reduce((acc: Record<string, string>, val: { ingredient_id: string, unit: string }) => {
    acc[val.ingredient_id] = val.unit;
    return acc;
  }, {} as { [key: string]: string; });
};

export async function createNewIngredient(url: string, name: string): Promise<string> {
  const newIngredient = await axiosInstance.post(`${url}/ingredients`, 
    { name: name }, 
    {
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + (localStorage.getItem("token") as string)
      }
    }
  );
  return newIngredient.data.id;
}
