def appointment_template(user_name, doctor, date, time):
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 8px;">Appointment Confirmed</h2>
    
        <p style="color: #333333; font-size: 15px;">Hello <b>{user_name}</b>,</p>
    
        <p style="color: #555555; font-size: 14px;">Your appointment has been successfully confirmed.</p>
    
        <table style="border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 14px;">
            <tr>
                <td style="padding: 8px 0; color: #555555; width: 80px;"><b>Doctor</b></td>
                <td style="padding: 8px 0; color: #2c3e50;">: {doctor}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #555555;"><b>Date</b></td>
                <td style="padding: 8px 0; color: #2c3e50;">: {date}</td>
            </tr>
            <tr>
                <td style="padding: 8px 0; color: #555555;"><b>Time</b></td>
                <td style="padding: 8px 0; color: #2c3e50;">: {time}</td>
            </tr>
        </table>
    
        <p style="color: #777777; font-size: 14px; margin-top: 20px;">Thank you for choosing our service.</p>
    </div>
    """


def registration_template(user_name):
        return f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px; background-color: #ffffff;">
                <div style="background-color: #0284c7; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">MediCare</h1>
                </div>
        
                <div style="padding: 20px; color: #334155;">
                    <h2 style="color: #0f172a; margin-top: 0;">Welcome, { user_name }! 🎉</h2>
                    <p>Thank you for registering with <b>MediCare Pro</b>. Your account has been successfully created.</p>
        
                    <p>You can now log in to access your dashboard, book appointments with doctors, and manage your health records seamlessly.</p>
        
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://clinical-system.com/login" style="background-color: #0284c7; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; display: inline-block;">Log In to Your Account</a>
                    </div>
        
                    <p style="color: #64748b; font-size: 14px;">If you didn't create this account, please ignore this email or contact support.</p>
                </div>
        
                <div style="border-top: 1px solid #e2e8f0; padding-top: 15px; text-align: center; color: #94a3b8; font-size: 12px;">
                    &copy; 2026 MediCare . All rights reserved.
                </div>
            </div>  
        """

def caregiver_request_approval_template(user_name, verification_link):
        return f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px; background-color: #ffffff;">
            <div style="background-color: #0284c7; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">MediCare</h1>
            </div>
        
            <div style="padding: 25px; color: #334155;">
                <h2 style="color: #0f172a; margin-top: 0; font-size: 20px;">Caregiver Approval Request</h2>
                
                <p style="font-size: 15px; line-height: 1.5;">Hello,</p>
                
                <p style="font-size: 15px; line-height: 1.5;">A new request has been submitted for a caregiver approval on your MediCare Pro account.</p>
                
                <p style="font-size: 15px; line-height: 1.5;">Please review the request and click the button below to approve and verify this action:</p>
        
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{ verification_link }" style="background-color: #0284c7; color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 6px; font-weight: bold; font-size: 15px; display: inline-block;">Approve Caregiver Request</a>
                </div>
    
                <p style="font-size: 13px; color: #64748b; line-height: 1.4;">
                    If the button above doesn't work, copy and paste the following link into your browser:
                    <br>
                    <a href="{ verification_link }" style="color: #0284c7; word-break: break-all;">{ verification_link }</a>
                </p>
        
                <p style="font-size: 13px; color: #94a3b8; margin-top: 25px;">
                    If you did not initiate or expect this request, please ignore this email or contact support immediately.
                </p>
            </div>
        
            <div style="border-top: 1px solid #e2e8f0; padding-top: 15px; text-align: center; color: #94a3b8; font-size: 12px;">
                &copy; 2026 MediCare . All rights reserved.
            </div>
            </div>  
        """


def send_otp_template(otp_code):
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px; background-color: #ffffff;">
            <div style="background-color: #0284c7; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">MediCare</h1>
            </div>
        
            <div style="padding: 25px; color: #334155;">
                <h2 style="color: #0f172a; margin-top: 0; font-size: 20px;">Your Verification Code</h2>
                
                <p style="font-size: 15px; line-height: 1.5;">Hello,</p>
                
                <p style="font-size: 15px; line-height: 1.5;">Use the OTP code below to verify your account or complete your request on MediCare Pro:</p>
        
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background-color: #f1f5f9; border: 2px dashed #0284c7; padding: 15px 30px; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0284c7; display: inline-block; border-radius: 8px;">
                        { otp_code }
                    </div>
                </div>
        
                <p style="font-size: 14px; color: #ef4444; text-align: center; font-weight: 500;">
                    ⏰ This code will expire in 5 minutes.
                </p>
        
                <p style="font-size: 13px; color: #94a3b8; margin-top: 25px;">
                    If you did not request this verification code, please ignore this email. Do not share this code with anyone.
                </p>
            </div>
        
            <div style="border-top: 1px solid #e2e8f0; padding-top: 15px; text-align: center; color: #94a3b8; font-size: 12px;">
                &copy; 2026 MediCare Pro. All rights reserved.
            </div>
        </div>
    """
