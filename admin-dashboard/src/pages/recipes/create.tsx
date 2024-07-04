import { useApiUrl, useList, useSelect } from "@refinedev/core";
import { Recipe } from "../../interfaces";
import { axiosInstance } from "../../App";
import { Button, Form, Input, Select, Space, UploadFile, notification } from "antd";
import { Create, useForm, getValueFromEvent } from "@refinedev/antd";
import { PlusOutlined } from "@ant-design/icons";
import { IngredientForm, useIngToUnitDict, createNewIngredient } from "../ingredients";
import { useState, Fragment } from "react";
import { PicCarousel } from "./pic-carousel";

export const CreateRecipe = () => {
  const apiUrl = useApiUrl();
  const [pics, setPics] = useState<UploadFile[]>([]);

  const { options: cat_options } = useSelect({
    resource: "categories",
    optionLabel: "name",
    optionValue: "id"
  });

  const { formProps, saveButtonProps } = useForm<Recipe>();

  const ingToUnitDict = useIngToUnitDict();
  if (!ingToUnitDict) return <div/>;

  function finishHandler(values: Record<string, any>) {
    handleFinish(apiUrl, pics, values);
  }

  return (
    <Create saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical" onFinish={finishHandler}>
        <Form.Item label="Name" name="name">
          <Input />
        </Form.Item>

        <Form.Item label="Instructions" name="instructions">
          <Input.TextArea />
        </Form.Item>

        <Form.Item label="Category" name="category">
          <Select options={cat_options?.map((category) => ({
            key: category.value,
            value: category.value,
            label: category.label
          }))} />
        </Form.Item>

        <Form.List name="ingredients">
          {(fields, { add, remove }) => (
            <>
              {fields.map((field) => (
                <Fragment key={field.key}>
                  <IngredientForm
                    formProps={formProps} 
                    field={field} 
                    ingToUnitDict={ingToUnitDict}
                    remove={() => remove(field.name)}
                  />
                </Fragment>
              ))}

              <Form.Item>
                <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                  Add Ingredient
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>

        <Form.Item label="Pictures">
          <Form.Item
            name="pictures"
            valuePropName="fileList"
            getValueFromEvent={getValueFromEvent}
            noStyle
          >
            <PicCarousel initialFileList={[]} onFileListChange={setPics} />
          </Form.Item>
        </Form.Item>
      </Form>
    </Create>
  );
};

const handleFinish = async (apiUrl: string, pics: UploadFile[], values: Record<string, any>) => {
  try {
    const formData = new FormData();
    for (const key in values) {
      if (key === "ingredients") {
        var temp = "";
        // fills temp out one ingredient at a time (example of one ingredient: "1, 1, kg;")
        for (const ingredient of values[key]) {
          // fills out temp with either id, qty, or unit (int or int or string)
          for (const ingredientKey in ingredient) {
            if (ingredientKey === "id") {
              if (ingredient[ingredientKey][0] === "*") {
                temp += ((await createNewIngredient(apiUrl, ingredient[ingredientKey].slice(1))).valueOf() + ", ");
              } else if (ingredient[ingredientKey][0] === "#") {
                temp += (ingredient[ingredientKey].slice(1) + ", ");
              }
            } else {
              temp += ingredient[ingredientKey] + ", ";
            }
          }
          temp = temp.slice(0, -2) + ";";
        }
        formData.append("ingredients", temp);
      } else if (key === "pictures") {
        if (pics.length > 0) {
          pics.forEach((file: any) => {
            formData.append(key, file.originFileObj);
          });
        } else {
          formData.append(key, "");
        }
      } else {
        formData.append(key, values[key]);
      }
    }
    const response = await axiosInstance.post(`${apiUrl}/recipes`, formData, {
      headers: {
        "Authorization": "Bearer " + (localStorage.getItem("token") as string)
      }
    });
    if (!response.status.toString().startsWith("2")) {
      throw new Error(`The server responded with a status code of ${response.status}.`);
    }
    notification.success({
      message: "Recipe created successfully!",
      description: `Status: ${response.status}`,
    });
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  } catch (error) {
    console.error("error " + error);
    notification.error({
      message: "Oops, something went wrong!",
      description: (error as Error).message,
    });
  }
};
