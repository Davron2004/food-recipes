import { Fragment, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { axiosInstance } from "../../App";

import { useForm, getValueFromEvent, Edit } from "@refinedev/antd";
import { useSelect, useApiUrl, useOne } from "@refinedev/core";

import { Button, Form, Input, Select, UploadFile, notification } from "antd";
import { PlusOutlined } from "@ant-design/icons";

import { IngredientForm, createNewIngredient, useIngToUnitDict } from "../ingredients";
import { PicCarousel } from "./pic-carousel";
import { Recipe } from "../../interfaces";


export const EditRecipe = () => {
  const { id } = useParams<{ id: string }>();

  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [newFiles, setNewFiles] = useState<UploadFile[]>([]);

  const ingToUnitDict = useIngToUnitDict();

  const navigate = useNavigate();
  const apiUrl = useApiUrl();

  const { options: cat_options } = useSelect({
    resource: "categories",
    optionLabel: "name",
    optionValue: "id"
  });

  const { formProps, saveButtonProps } = useForm<Recipe>();

  const { data: rec, isSuccess } = useOne<Recipe>({ resource: "recipes", id });

  useEffect(() => {
    if (!rec) return;
    const pics = rec.data.pictures.map((pic_id) => ({
      uid: pic_id,
      name: pic_id,
      status: 'done',
      url: `${apiUrl}/pictures/${pic_id}`,
    } as UploadFile));
  
    setFileList(pics);
  }, [rec]);

  if (!isSuccess || !ingToUnitDict) return <div/>;

  const ings = rec.data.ingredients.map((ingredient) => ({
    id: ingredient.ingredient.id,
    qty: ingredient.qty,
    unit: ingredient.unit
  }));
  
  const recipe = {
    name: rec.data.name,
    instructions: rec.data.instructions,
    category: rec.data.category.id,
    ingredients: ings,
    pictures: fileList,
  };

  const cat_table_opts = cat_options?.map((category) => ({
    key: category.value,
    value: category.value,
    label: category.label
  }));

  const handleFileListChange = (newFileList: UploadFile[]) => {
    // Filter out the new files from the updated file list
    const newFiles = newFileList.filter(file => !file.url);
    const notRemovedFiles = newFileList.filter(file => file.url);
    setNewFiles(newFiles);
    setFileList(notRemovedFiles);
  };

  const finishHandler = async (values: Record<string, any>) => {
    handleFinish(apiUrl, id, newFiles, JSON.stringify(fileList.map((file: any) => file.uid)), values);
    navigate("/recipes");
  }

  return (
    <Edit saveButtonProps={saveButtonProps}>
      <Form
        {...formProps}
        layout="vertical"
        initialValues={recipe}
        onFinish={finishHandler}
      >
        <Form.Item label="Name" name="name">
          <Input />
        </Form.Item>

        <Form.Item label="Instructions" name="instructions">
          <Input.TextArea />
        </Form.Item>

        <Form.Item label="Category" name="category">
          <Select options={cat_table_opts} />
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
                <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}> Add Ingredient </Button>
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
            <PicCarousel initialFileList={recipe.pictures} onFileListChange={handleFileListChange} />
          </Form.Item>
        </Form.Item>
      </Form>
    </Edit>
  );
};

const handleFinish = async (apiUrl: string, recipeId: string | undefined, newFiles: UploadFile[], oldPics: string, values: Record<string, any>) => {
  try {
    const formData = new FormData();
    for (const key in values) {
      if (key === "ingredients") {
        let temp = "";
        for (const ingredient of values[key]) {
          for (const ingredientKey in ingredient) {
            if (ingredientKey === "id") {
              if (ingredient[ingredientKey][0] === "*") {
                temp += ((await createNewIngredient(apiUrl, ingredient[ingredientKey].slice(1))).valueOf() + ", ");
              } else if (ingredient[ingredientKey][0] === "#") {
                temp += (ingredient[ingredientKey].slice(1) + ", ");
              } else {
                // MAYBE buggy in yet undiscovered edge cases
                temp += ingredient[ingredientKey] + ", "
              }
            } else {
              temp += ingredient[ingredientKey] + ", ";
            }
          }
          temp = temp.slice(0, -2) + ";";
        }
        formData.append("ingredients", temp);
      } else if (key === "pictures") {
        if (newFiles.length > 0) {
          newFiles.forEach((file: any) => {
            formData.append(key, file.originFileObj);
          });
        } else {
          formData.append(key, "");
        }
      } else {
        formData.append(key, values[key]);
      }
    }
    formData.append("pics_to_remain", oldPics);

    const response = await axiosInstance.put(`${apiUrl}/recipes/${recipeId}`, formData, {
      headers: {
        "Authorization": "Bearer " + (localStorage.getItem("token") as string)
      }
    });
    if (!response.status.toString().startsWith("2")) {
      throw new Error(`The server responded with a status code of ${response.status}.`);
    }
    notification.success({
      message: "Recipe changed successfully!",
      description: `Status: ${response.status}.`,
    });
    return true;
  } catch (error) {
    console.error("error " + error);
    notification.error({
      message: "Oops, something went wrong!",
      description: (error as Error).message,
    });
  }
};