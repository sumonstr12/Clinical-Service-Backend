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