import React, { useState } from 'react';

import type { GetProp, UploadFile, UploadProps } from 'antd';

import { Image, Upload } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

type FileType = Parameters<GetProp<UploadProps, 'beforeUpload'>>[0];

const getBase64 = (file: FileType): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
  });

type PicCarouselProps = {
  initialFileList?: UploadFile[];
  onFileListChange?: (fileList: UploadFile[]) => void;
};

export const PicCarousel: React.FC<PicCarouselProps> = ({ initialFileList = [], onFileListChange }) => {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [fileList, setFileList] = useState<UploadFile[]>(initialFileList);

  const handlePreview = async (file: UploadFile) => {
    // TODO might need to change .url to .name
    if (!file.url && !file.preview) {
      file.preview = await getBase64(file.originFileObj as FileType);
    }

    setPreviewImage(file.url || (file.preview as string));
    setPreviewOpen(true);
  };

  const handleChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);
  
    // Pass the updated file list to the parent component
    if (onFileListChange) {
      onFileListChange(newFileList);
    }
  };

  return (
    <>
      <Upload
        action=""
        beforeUpload={() => false}
        listType="picture-card"
        fileList={fileList}
        onPreview={handlePreview}
        onChange={handleChange}
      >
        <button style={{ border: 0, background: 'none' }} type="button">
            <PlusOutlined />
            <div style={{ marginTop: 8 }}>Upload</div>
        </button>
      </Upload>
      {previewImage && (
        <Image
          wrapperStyle={{ display: 'none' }}
          preview={{
            visible: previewOpen,
            onVisibleChange: (visible) => setPreviewOpen(visible),
            afterOpenChange: (visible) => !visible && setPreviewImage(''),
          }}
          src={previewImage}
        />
      )}
    </>
  );
};