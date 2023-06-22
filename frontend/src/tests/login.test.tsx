import { fireEvent, render, screen } from '@testing-library/react'
import Login from 'pages/Login'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

Object.defineProperty(URL, 'createObjectURL', {
  writable: true,
  value: jest.fn(),
})
test('page Login', async () => {
  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>,
  )
  expect(screen.getByTestId('title')).toHaveTextContent(
    'Sign in to your account',
  )
  fireEvent.change(screen.getByTestId('email'), {
    target: { value: 'admin@gmail.com' },
  })
  expect((screen.getByTestId('email') as any).value).toBe('admin@gmail.com')
  fireEvent.change(screen.getByTestId('password'), {
    target: { value: 'Admin12@' },
  })
  expect((screen.getByTestId('password') as any).value).toBe('Admin12@')

  //check required input
  fireEvent.change(screen.getByTestId('email'), { target: { value: '' } })
  expect((screen.getByTestId('email') as any).value).toBe('')
  expect(screen.getByTestId('error-email')).toHaveTextContent(
    'This field is required',
  )
  fireEvent.change(screen.getByTestId('password'), { target: { value: '' } })
  expect((screen.getByTestId('password') as any).value).toBe('')
  expect(screen.getByTestId('error-password')).toHaveTextContent(
    'This field is required',
  )

  //submit wrong account
  fireEvent.change(screen.getByTestId('email'), {
    target: { value: 'admin@gmail.com' },
  })
  fireEvent.change(screen.getByTestId('password'), {
    target: { value: 'Admin12' },
  })
  await fireEvent.click(screen.getByTestId('button-submit'))
  await screen.findByText('Email or password is wrong')

  expect(screen.getByTestId('error-email')).toHaveTextContent(
    'Email or password is wrong',
  )
})
