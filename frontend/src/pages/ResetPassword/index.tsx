import { Box, Stack, styled, Typography } from '@mui/material'
import { ChangeEvent, FormEvent, useState } from 'react'
import {resetPassword} from "../../api/auth";

const regexEmail = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/

const ResetPassword = () => {

    const [errors, setErrors] = useState<{ [key: string]: string }>({
        email: '',
    })
    const [values, setValues] = useState<{ email: string }>({
        email: '',
    })

    const onReset = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        const errorCheck = validateSubmit()
        if (errors.email || errorCheck) return
        try {
            await resetPassword(values.email)
            alert(` You'll receive a link to reset your password at ${values.email}. Pls check you mail!`)
        }
        catch {
            alert('Email does not exist!')
        }
    }

    const validateEmail = (value: string): string => {
        if(!value) return 'This field is required'
        if(value.length > 255) return 'The text may not be longer than 255 characters'
        if(!regexEmail.test(value)) return 'This field is validate'
        return ''
    }

    const validateSubmit = () => {
        let errors = { email: '' }
        errors.email = validateEmail(values.email)
        setErrors(errors)
        return errors.email
    }

    const onChangeValue = (event: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = event.target
        const error = validateEmail(value)
        setValues({ ...values, [name]: value })
        setErrors({ ...errors, [name]: error })
    }

    return (
        <LoginWrapper>
            <LoginContent>
                <Heading>Forgot password?</Heading>
                <Title>No worries, we'll send you reset instructions.</Title>
                <FormSignUp autoComplete="off" onSubmit={onReset}>
                    <Box sx={{ position: 'relative' }}>
                        <LabelField>
                            Email<LableRequired>*</LableRequired>
                        </LabelField>
                        <Input
                            autoComplete="off"
                            error={!!errors.email}
                            name="email"
                            onChange={onChangeValue}
                            value={values.email}
                            placeholder="Enter your email"
                        />
                        <TextError>{errors.email}</TextError>
                    </Box>
                    <Stack
                        flexDirection="row"
                        gap={2}
                        mt={3}
                        alignItems="center"
                        justifyContent="flex-end"
                    >
                        <ButtonLogin type="submit">Reset Password</ButtonLogin>
                    </Stack>
                </FormSignUp>
            </LoginContent>
        </LoginWrapper>
    )
}

const LoginWrapper = styled(Box)({
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
})

const LoginContent = styled(Box)({
    padding: 30,
    boxShadow: '2px 1px 3px 1px rgba(0,0,0,0.1)',
    borderRadius: 4,
})

const Heading = styled(Typography)({
    fontSize: 22,
    textAlign: 'center',
    fontWeight: 600,
})

const Title = styled(Typography)({
    textAlign: 'center',
    marginBottom: 24,
    fontSize: 12,
    color: 'rgba(0, 0, 0, 0.65)',
})

const FormSignUp = styled('form')({})

const LabelField = styled(Typography)({
    fontSize: 14,
})

const LableRequired = styled('span')({
    color: 'red',
    fontSize: 14,
    marginLeft: 2,
})

const Input = styled('input', {
    shouldForwardProp: (props) => props !== 'error',
})<{ error: boolean }>(({ error }) => {
    return {
        width: 250,
        height: 24,
        borderRadius: 4,
        border: '1px solid',
        borderColor: error ? 'red' : '#d9d9d9',
        padding: '5px 10px',
        marginBottom: 22,
        transition: 'all 0.3s',
        outline: 'none',
        ':focus, :hover': {
            borderColor: '#1677ff',
        },
    }
})

const ButtonLogin = styled('button')({
    backgroundColor: '#283237',
    color: '#ffffff',
    borderRadius: 4,
    border: 'none',
    outline: 'none',
    padding: '10px 20px',
    cursor: 'pointer',
})

const TextError = styled(Typography)({
    fontSize: 12,
    color: 'red',
    position: 'absolute',
    bottom: 4,
})

const WrapperMes = styled(Box)(({})=>({

}))

export default ResetPassword
