<template>
    <FileUploader
      :file-types="image_type"
      class="text-base"
      @success="
        (file) => {
          $emit('upload', file.file_url)
        }
      "
    >
      <template v-slot="{ progress, uploading, openFileSelector }">
        <div class="flex items-end space-x-1">
          <Button @click="openFileSelector" style="background-color: #4e60ac !important; border-color: #4e60ac !important; color: white !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important;">
            {{
              uploading
                ? `Uploading ${progress}%`
                : image_url
                  ? 'Change'
                  : 'Upload'
            }}
          </Button>
          <Button v-if="image_url" @click="$emit('remove')" style="background-color: #82868f !important; border-color: #82868f !important; color: white !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important;">Remove</Button>
        </div>
      </template>
    </FileUploader>
  </template>
  <script setup>
  import { FileUploader, Button } from 'frappe-ui'
  
  const prop = defineProps({
    image_url: String,
    image_type: {
      type: String,
      default: 'image/*',
    },
    label: {
      type: String,
      default: '',
    },
  })
  const emit = defineEmits(['upload', 'remove'])
  </script>
  