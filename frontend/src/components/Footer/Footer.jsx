import React from 'react';
import {   TrendingUp,Mail, Phone, Globe, MapPin } from 'lucide-react';
import { FaInstagramSquare,FaTwitter,FaGithub,FaLinkedin  } from "react-icons/fa";

const Footer = ({onNavigate}) => {
  return (
    <footer className="w-full text-gray-300 font-sans mt-12 border-t border-gray-800">
     
      <div className="bg-[#7c3aed] text-white py-4 px-6 md:px-12 flex flex-col md:flex-row justify-between items-center gap-4">
        <span className="text-sm font-medium">Get connected with us on social networks!</span>
        <div className="flex space-x-6">
         
          <a href="https://twitter.com/athenura_in" className="hover:text-gray-200 transition-colors"><FaTwitter size={18} /></a>
          <a href=" https://share.google/Fz19XOGf0Cvvlf7QB" className="hover:text-gray-200 transition-colors"><FaLinkedin size={18} /></a>
          <a href="https://share.google/4FWmN9qZuMgRjHvo3" className="hover:text-gray-200 transition-colors"><FaInstagramSquare size={18} /></a>

        </div>
      </div>


      <div className="bg-[#0B0F19] py-12 px-6 md:px-12 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm">
      
        <div className="space-y-4">
          <h6 className="text-white font-bold tracking-wider uppercase text-xs border-b-2 border-[#7c3aed] w-16 pb-1">
            Athenura
          </h6>
          <p className="text-gray-400 leading-relaxed">
            Empowering investors and organizations with advanced Data Science & Analytics platforms. We specialize in tracking funding trends and predictive ecosystem models.
          </p>
        </div>

        
        <div className="space-y-4">
          <h6 className="text-white font-bold tracking-wider uppercase text-xs border-b-2 border-[#7c3aed] w-16 pb-1">
            Products
          </h6>
          <ul className="space-y-2 text-gray-400">
            <li><button  onClick={() => onNavigate("Trends")}  className="hover:text-white transition-colors">Trend Analysis</button></li>
            <li><button  onClick={() => onNavigate("Predict")} className="hover:text-white transition-colors">Predictive Analytics</button></li>
            <li><button  onClick={() => onNavigate("Sectors")} className="hover:text-white transition-colors">Sector Analytics</button></li>
            <li><button  onClick={() => onNavigate("Reports")} className="hover:text-white transition-colors">Automated Reports</button></li>
          </ul>
        </div>

      
        <div className="space-y-4">
          <h6 className="text-white font-bold tracking-wider uppercase text-xs border-b-2 border-[#7c3aed] w-16 pb-1">
            Useful Links
          </h6>
          <ul className="space-y-2 text-gray-400">
            <li><button  onClick={() => onNavigate("Dashboard")} className="hover:text-white transition-colors">Main Dashboard</button></li>
        
            <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-white transition-colors">Help & Support</a></li>
          </ul>
        </div>

     
        <div className="space-y-4">
          <h6 className="text-white font-bold tracking-wider uppercase text-xs border-b-2 border-[#7c3aed] w-16 pb-1">
            Contact
          </h6>
          <ul className="space-y-3 text-gray-400">
            <li className="flex items-center gap-2">
              <MapPin size={16} className="text-[#7c3aed]" />
              <span>India</span>
            </li>
            <li className="flex items-center gap-2">
              <Mail size={16} className="text-[#7c3aed]" />
              <a href="mailto:official@athenura.in" className="hover:text-white">official@athenura.in</a>
            </li>
            <li className="flex items-center gap-2">
              <Phone size={16} className="text-[#7c3aed]" />
              <a href="tel:+919835051934" className="hover:text-white">+91 98350 51934</a>
            </li>
            <li className="flex items-center gap-2">
              <Globe size={16} className="text-[#7c3aed]" />
              <a href="https://www.athenura.in" target="_blank" rel="noreferrer" className="hover:text-white">www.athenura.in</a>
            </li>
          </ul>
        </div>
      </div>

      
      <div className="bg-[#070a10] py-4 text-center text-xs text-gray-500 border-t border-gray-900">
        <span>© 2026 Copyright: </span>
        <a href="https://www.athenura.in" className="text-[#7c3aed] hover:underline font-semibold">Athenura.in</a>
      </div>
    </footer>
  );
};

export default Footer;
