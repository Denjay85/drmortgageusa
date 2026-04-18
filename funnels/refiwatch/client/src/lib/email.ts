import { Lead } from "@shared/schema";

export async function sendLeadNotification(lead: Lead): Promise<void> {
  const RESEND_API_KEY = process.env.RESEND_API_KEY || process.env.VITE_RESEND_API_KEY;
  const ADMIN_EMAIL = process.env.ADMIN_EMAIL || process.env.VITE_ADMIN_EMAIL || "admin@drmortgageusa.com";
  const FROM_EMAIL = process.env.FROM_EMAIL || process.env.VITE_FROM_EMAIL || "noreply@drmortgageusa.com";
  
  if (!RESEND_API_KEY) {
    console.warn("RESEND_API_KEY not configured - email notification skipped");
    return;
  }

  const emailHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>New Rate Watch Lead</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff;">
        <!-- Header -->
        <div style="background: hsl(217, 91%, 60%); padding: 30px; text-align: left;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 20px;">
              DM
            </div>
            <div>
              <h1 style="color: white; margin: 0; font-size: 18px; font-weight: 600;">DrMortgageUSA</h1>
              <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 14px;">New Lead Notification</p>
            </div>
          </div>
        </div>
        
        <!-- Body -->
        <div style="padding: 32px;">
          <h2 style="color: #333; margin: 0 0 16px 0; font-size: 20px;">🎯 New Rate Watch Lead Submitted</h2>
          
          <p style="color: #666; margin-bottom: 24px;">
            A new lead has been submitted to your Rate Watch system. Here are the details:
          </p>
          
          <!-- Lead Details -->
          <div style="background: #f8fafc; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
            <h3 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 600; color: #333;">Lead Information</h3>
            <table style="width: 100%; border-collapse: collapse;">
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Name:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">${lead.name}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Email:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">${lead.email}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Phone:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">${lead.phone}</td>
              </tr>
              <tr>
                <td colspan="2" style="border-top: 1px solid #e2e8f0; padding-top: 12px; margin-top: 8px;"></td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Year Bought:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">${lead.yearBought}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Monthly Savings Goal:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px; color: hsl(142, 76%, 36%);">$${lead.savingsGoal}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Current Rate:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">${lead.currentRate || 'Not provided'}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Consent Given:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px; color: hsl(142, 76%, 36%);">✓ Yes</td>
              </tr>
            </table>
          </div>
          
          <!-- Action Buttons -->
          <div style="margin-bottom: 24px;">
            <a href="${process.env.FRONTEND_URL || 'http://localhost:5000'}/#admin" 
               style="display: inline-block; background: hsl(217, 91%, 60%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px; margin-right: 12px;">
              View in Dashboard
            </a>
            <a href="mailto:${lead.email}" 
               style="display: inline-block; background: transparent; color: hsl(217, 91%, 60%); padding: 12px 24px; text-decoration: none; border: 1px solid hsl(214, 32%, 91%); border-radius: 8px; font-weight: 500; font-size: 14px;">
              Contact Lead
            </a>
          </div>
          
          <!-- Timestamp -->
          <div style="border-top: 1px solid #e2e8f0; padding-top: 24px; font-size: 14px; color: #666;">
            <p style="margin: 0;">Submitted: <strong>${new Date(lead.createdAt).toLocaleString()}</strong></p>
            <p style="margin: 4px 0 0 0;">Source: <strong>${lead.source}</strong></p>
          </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f8fafc; padding: 24px; border-top: 1px solid #e2e8f0; text-align: center;">
          <p style="margin: 0; font-size: 12px; color: #666;">
            This is an automated notification from DrMortgageUSA Rate Watch System.<br/>
            NMLS# 2018381 | Home First Lending
          </p>
        </div>
      </div>
    </body>
    </html>
  `;

  try {
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: FROM_EMAIL,
        to: [ADMIN_EMAIL],
        subject: `🎯 New Rate Watch Lead: ${lead.name}`,
        html: emailHtml,
      }),
    });

    if (!response.ok) {
      throw new Error(`Resend API error: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    console.log("Email notification sent successfully:", result.id);
  } catch (error) {
    console.error("Failed to send email notification:", error);
    throw error;
  }
}

interface RefinanceAlertData {
  to: string;
  name: string;
  currentRate: string;
  newRate: string;
  monthlySavings: string;
  totalInterestSaved: string;
  breakEvenMonths: number;
}

export async function sendRefinanceAlert(data: RefinanceAlertData): Promise<void> {
  const RESEND_API_KEY = process.env.RESEND_API_KEY || process.env.VITE_RESEND_API_KEY;
  const FROM_EMAIL = process.env.FROM_EMAIL || process.env.VITE_FROM_EMAIL || "noreply@drmortgageusa.com";
  
  if (!RESEND_API_KEY) {
    console.warn("RESEND_API_KEY not configured - email notification skipped");
    return;
  }

  const emailHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Refinance Alert - Rate Watch</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff;">
        <!-- Header -->
        <div style="background: hsl(142, 76%, 36%); padding: 30px; text-align: left;">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 48px; height: 48px; border-radius: 12px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 20px;">
              ✓
            </div>
            <div>
              <h1 style="color: white; margin: 0; font-size: 18px; font-weight: 600;">DrMortgageUSA Rate Watch</h1>
              <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 14px;">Refinance Opportunity Alert</p>
            </div>
          </div>
        </div>
        
        <!-- Body -->
        <div style="padding: 32px;">
          <h2 style="color: #333; margin: 0 0 16px 0; font-size: 20px;">🎉 Great News, ${data.name}!</h2>
          
          <p style="color: #666; margin-bottom: 24px; font-size: 16px;">
            Mortgage rates have dropped, and refinancing now meets your savings goal! Here's what you could save:
          </p>
          
          <!-- Savings Highlight -->
          <div style="background: linear-gradient(135deg, hsl(142, 76%, 36%) 0%, hsl(142, 76%, 46%) 100%); border-radius: 12px; padding: 24px; margin-bottom: 24px; color: white;">
            <div style="text-align: center;">
              <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Estimated Monthly Savings</div>
              <div style="font-size: 48px; font-weight: bold; margin-bottom: 4px;">$${data.monthlySavings}</div>
              <div style="font-size: 14px; opacity: 0.9;">per month</div>
            </div>
          </div>
          
          <!-- Details -->
          <div style="background: #f8fafc; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
            <h3 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 600; color: #333;">Refinance Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Your Current Rate:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">${data.currentRate}%</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">New Market Rate:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px; color: hsl(142, 76%, 36%);">${data.newRate}%</td>
              </tr>
              <tr>
                <td colspan="2" style="border-top: 1px solid #e2e8f0; padding-top: 12px; margin-top: 8px;"></td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Monthly Savings:</td>
                <td style="padding: 8px 0; font-weight: 600; font-size: 14px; color: hsl(142, 76%, 36%);">$${data.monthlySavings}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Total Interest Saved:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">$${data.totalInterestSaved}</td>
              </tr>
              <tr>
                <td style="padding: 8px 0; color: #666; font-size: 14px;">Break-Even Point:</td>
                <td style="padding: 8px 0; font-weight: 500; font-size: 14px;">${data.breakEvenMonths} months</td>
              </tr>
            </table>
          </div>
          
          <!-- Why This Matters -->
          <div style="margin-bottom: 24px;">
            <h3 style="margin: 0 0 12px 0; font-size: 16px; font-weight: 600; color: #333;">Why This Matters</h3>
            <ul style="color: #666; margin: 0; padding-left: 20px; font-size: 14px;">
              <li style="margin-bottom: 8px;">You'll save $${data.monthlySavings} every month on your mortgage payment</li>
              <li style="margin-bottom: 8px;">You'll recoup closing costs in just ${data.breakEvenMonths} months</li>
              <li style="margin-bottom: 8px;">Over the life of your loan, you'll save over $${data.totalInterestSaved} in interest</li>
            </ul>
          </div>
          
          <!-- CTA -->
          <div style="background: #fef3c7; border-left: 4px solid hsl(45, 93%, 47%); padding: 16px; margin-bottom: 24px; border-radius: 4px;">
            <p style="margin: 0; color: #92400e; font-size: 14px;">
              <strong>⏰ Don't wait!</strong> Rates can change quickly. Schedule a consultation now to lock in these savings.
            </p>
          </div>
          
          <!-- Action Button -->
          <div style="text-align: center; margin-bottom: 24px;">
            <a href="https://calendly.com/dennis-ross-myhome1st/30min" 
               style="display: inline-block; background: hsl(217, 91%, 60%); color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px;">
              Schedule Free Consultation
            </a>
          </div>
          
          <!-- Footer Note -->
          <div style="border-top: 1px solid #e2e8f0; padding-top: 16px; font-size: 12px; color: #666;">
            <p style="margin: 0;">
              This alert is based on current market rates and your information. Actual savings may vary based on your specific loan details, credit profile, and closing costs. Contact us for a personalized refinance analysis.
            </p>
          </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f8fafc; padding: 24px; border-top: 1px solid #e2e8f0; text-align: center;">
          <p style="margin: 0; font-size: 12px; color: #666;">
            This is an automated notification from DrMortgageUSA Rate Watch System.<br/>
            NMLS# 2018381 | Home First Lending
          </p>
          <p style="margin: 8px 0 0 0; font-size: 12px; color: #999;">
            You're receiving this because you signed up for Rate Watch alerts.<br/>
            To update preferences or unsubscribe, reply to this email.
          </p>
        </div>
      </div>
    </body>
    </html>
  `;

  try {
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: FROM_EMAIL,
        to: [data.to],
        subject: `🎉 Rate Watch Alert: Save $${data.monthlySavings}/month by Refinancing!`,
        html: emailHtml,
      }),
    });

    if (!response.ok) {
      throw new Error(`Resend API error: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    console.log("Refinance alert email sent successfully:", result.id);
  } catch (error) {
    console.error("Failed to send refinance alert email:", error);
    throw error;
  }
}
