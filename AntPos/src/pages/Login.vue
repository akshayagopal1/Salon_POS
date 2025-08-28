<template>
  <div class="m-3 flex flex-row items-center justify-center" style="background-color: #f8f8fc !important; color: #82868f !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important; min-height: 100vh;">
    <Card title="Login to your FrappeUI App!" class="w-full max-w-md mt-4">
      <form class="flex flex-col space-y-2 w-full" @submit.prevent="submit">
        <Input
          required
          name="email"
          type="text"
          placeholder="johndoe@email.com"
          label="User ID"
        />
        <Input
          required
          name="password"
          type="password"
          placeholder="••••••"
          label="Password"
        />
        <Button :loading="session.login.loading" variant="solid" style="background-color: #4e60ac !important; border-color: #4e60ac !important; color: white !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important;"
          >Login</Button
        >
      </form>
    </Card>
  </div>
</template>

<script  setup>
import { useSessionStore } from '../data/session'

const session = useSessionStore()

function submit(e) {
  let formData = new FormData(e.target)
  session.login.submit({
    email: formData.get('email'),
    password: formData.get('password'),
  })
}
</script>
